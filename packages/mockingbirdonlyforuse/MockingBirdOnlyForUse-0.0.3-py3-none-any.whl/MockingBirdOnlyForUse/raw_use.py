from typing import Iterable
from encoder import inference as encoder
from synthesizer.inference import Synthesizer
from vocoder.wavernn import inference as rnn_vocoder
from vocoder.hifigan import inference as gan_vocoder
from pathlib import Path
import numpy as np
import torch
import librosa
import re
import io
from scipy.io.wavfile import write


def process_text(texts: Iterable[str]) -> list[str]:
    punctuation = "！，。、,"  # punctuate and split/clean text
    processed_texts = []
    for text in texts:
        for processed_text in re.sub(r"[{}]+".format(punctuation), "\n", text).split("\n"):
            if processed_text:
                processed_texts.append(processed_text.strip())
    return processed_texts


class Params:
    def __init__(
        self,
        text,
        recoder_path,
        synt_path: Path = None,
        min_stop_token: int = 4,
        steps: int = 4,
        style_idx: int = -1,
        save_path: Path = None,
        vocoder: str = "HifiGan",
        seed: int = None,
    ) -> None:
        """使用MockingBird时自定义的参数

        Args:
            text (str): 生成语音的目标文字
            synt_path (Path, optional): Synthesizer模型，不填写时使用默认目录的第一个. Defaults to None.
            min_stop_token (int, optional): Accuracy(精度) 范围3~9. Defaults to 4.
            steps (int, optional): MaxLength(最大句长) 范围1~10. Defaults to 4.
            style_idx (int, optional): Style 范围 -1~9. Defaults to -1.
            save_path (Path, optional): 生成后保存到文件的路径，不填会返回ByteIO类型，填上返回的是Path类型. Defaults to None.
            vocoder (str, optional): 选择Vocoder模型，影响不大，默认使用HifiGan，可选WaveRNN. Defaults to "HifiGan".
            seed (int, optional): 种子，不建议修改. Defaults to None.
        """
        self.seed = seed
        self.recoder = recoder_path
        if vocoder == "HifiGan":
            self.vocoder = gan_vocoder  # 速度较快
        else:
            self.vocoder = rnn_vocoder
        self.text = text
        self.synt_path = synt_path
        self.min_stop_token: int = min_stop_token
        self.steps: int = steps
        self.style_idx: int = style_idx
        self.save_path: Path = save_path

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        if value is None or isinstance(value, int):
            self._seed = value
        else:
            raise TypeError("Param seed must be a int value.")

    @property
    def steps(self):
        return self._steps

    @steps.setter
    def steps(self, value):
        if isinstance(value, int):
            if 1 <= value <= 10:
                self._steps = value
            else:
                raise ValueError("1 <= steps <= 10.")
        else:
            raise TypeError("Param steps must be a int value.")

    @property
    def min_token(self):
        return self._min_token

    @min_token.setter
    def min_token(self, value):
        if isinstance(value, int):
            if 3 <= value <= 9:
                self._min_token = value
            else:
                raise ValueError("3 <= min_token <= 9.")
        else:
            raise TypeError("Param min_token must be a int value.")

    @property
    def style_idx(self):
        return self._style_idx

    @style_idx.setter
    def style_idx(self, value):
        if isinstance(value, int):
            if -1 <= value <= 9:
                self._style_idx = value
            else:
                raise ValueError("-1 <= style_idx <= 9.")
        else:
            raise TypeError("Param style_idx must be a int value.")


_synthesizers_cache = {}
_cache_encodered_wav = {}


class MockingBird:
    @classmethod
    def init(cls, encoder_path, vocoder_path, vocoder_type):
        cls.load_encoder(encoder_path)
        cls.load_vocoder(vocoder_path, vocoder_type)

    @classmethod
    def load_encoder(cls, encoder_path: Path):
        encoder.load_model(encoder_path)

    @classmethod
    def load_vocoder(cls, vocoder_path: Path, vocoder_type: str):
        if vocoder_type.lower() == "wavernn":
            rnn_vocoder.load_model(vocoder_path)
        elif vocoder_type.lower() == "hifigan":
            gan_vocoder.load_model(vocoder_path)

    @classmethod
    def synthesize(cls, params: Params):
        global _synthesizers_cache

        if params.seed is not None:
            torch.manual_seed(params.seed)
            _synthesizers_cache = {}

        if not params.synt_path:
            print("NO synthsizer is specified, try cache.")
            params.synt_path = _synthesizers_cache.items()[0]

        if _synthesizers_cache.get(params.synt_path) is None:
            current_synt = Synthesizer(Path(params.synt_path))
            _synthesizers_cache[params.synt_path] = current_synt
        else:
            current_synt = _synthesizers_cache[params.synt_path]
        print(f"using synthesizer model: {params.synt_path}")

        # TODO load wav
        # Load input wav
        global _cache_encodered_wav
        embed = _cache_encodered_wav.get(params.recoder, None)
        if embed is None:
            wav, sample_rate = librosa.load(params.recoder)
            # write("temp.wav", sample_rate, wav) #Make sure we get the correct wav

            encoder_wav = encoder.preprocess_wav(wav, sample_rate)
            embed, _, _ = encoder.embed_utterance(encoder_wav, return_partials=True)
            _cache_encodered_wav[params.recoder] = embed

        texts = process_text(filter(None, params.text.split("\n")))

        # synthesize and vocode
        embeds = [embed] * len(texts)
        specs = current_synt.synthesize_spectrograms(
            texts,
            embeds,
            style_idx=params.style_idx,
            min_stop_token=params.min_stop_token,
            steps=params.steps * 200,
        )
        spec = np.concatenate(specs, axis=1)
        # breaks = [spec.shape[1] for spec in specs]
        # self.current_generated = (speaker_name, spec, breaks, None)
        wav = params.vocoder.infer_waveform(spec)
        wav = wav / np.abs(wav).max() * 0.97
        # Return cooked wav
        if params.save_path:
            write(params.save_path, Synthesizer.sample_rate, wav.astype(np.float32))
            return params.save_path
        out = io.BytesIO()
        write(out, Synthesizer.sample_rate, wav.astype(np.float32))
        return out

    @classmethod
    def vocoder(cls, params: Params):
        global _synthesizers_cache

        if params.seed is not None:
            torch.manual_seed(params.seed)
            _vocoder_cache = []

        if _synthesizers_cache.get(params.synt_path) is None:
            current_synt = Synthesizer(Path(params.synt_path))
            _vocoder_cache[params.synt_path] = current_synt
        else:
            current_synt = _vocoder_cache[params.synt_path]
        print(f"using synthesizer model: {params.synt_path}")
        # def vocoder_progress(i, seq_len, b_size, gen_rate):
        #     real_time_factor = (gen_rate / Synthesizer.sample_rate) * 1000
        #     line = "Waveform generation: %d/%d (batch size: %d, rate: %.1fkHz - %.2fx real time)" \
        #            % (i * b_size, seq_len * b_size, b_size, gen_rate, real_time_factor)
        #     self.ui.log(line, "overwrite")
        #     self.ui.set_loading(i, seq_len)
        # wav = params.vocoder.infer_waveform(spec)

    @classmethod
    def genrator_voice(cls, params: Params):
        return cls.synthesize(params)


if __name__ == "__main__":
    params = Params("我爱你，你爱我", Path("temp.wav"))
    params.synt_path = "synthesizer/saved_models/azusa_200k.pt"
    params.save_path = "test.wav"
    MockingBird.init(
        Path(r"encoder\saved_models\pretrained.pt"),
        Path(r"vocoder\saved_models\pretrained\g_hifigan.pt"),
        "HifiGan",
    )
    out = MockingBird.genrator_voice(params)
