import logging
import os
import sys
import time

LOG_LEVEL = logging.INFO
OPEN_CONSOLE_LOG = True
OPEN_FILE_LOG = False
LOG_FILE_PATH = None
LOG_NAME = "null"


###############################################################################################################

# 初始化日志


def _create_logger(
    level=LOG_LEVEL,
    open_console=OPEN_CONSOLE_LOG,
    open_file=OPEN_FILE_LOG,
    path=LOG_FILE_PATH,
):
    logger = logging.getLogger("MockingBird")
    logger.setLevel(level)
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s")
    if open_console:
        hterm = logging.StreamHandler()
        hterm.setLevel(level)
        hterm.setFormatter(formatter)
        logger.addHandler(hterm)
    if open_file:
        if not os.path.exists(path):
            os.mkdir(path)
        hfile = logging.FileHandler(
            path + "/" + time.strftime("%Y-%m-%d", time.localtime()) + ".log",
            encoding="utf-8",
        )
        hfile.setLevel(level)
        hfile.setFormatter(formatter)
        logger.addHandler(hfile)
    return logger


class Logger:
    def __init__(
        self,
        level=LOG_LEVEL,
        open_console=OPEN_CONSOLE_LOG,
        open_file=OPEN_FILE_LOG,
        path=LOG_FILE_PATH,
    ) -> None:
        self.logger = _create_logger(level, open_console, open_file, path)

    def debug(self, msg):
        try:
            msg = "[{}][{}][{}] {}".format(
                os.path.basename(sys._getframe(1).f_code.co_filename),
                sys._getframe(1).f_code.co_name,
                sys._getframe(1).f_lineno,
                msg,
            )
        except:
            pass
        self.logger.debug(msg)
        return

    def info(self, msg):
        try:
            msg = "[{}][{}][{}] {}".format(
                os.path.basename(sys._getframe(1).f_code.co_filename),
                sys._getframe(1).f_code.co_name,
                sys._getframe(1).f_lineno,
                msg,
            )
        except:
            pass
        self.logger.info(msg)
        return

    def error(self, msg):
        try:
            msg = "[{}][{}][{}] {}".format(
                os.path.basename(sys._getframe(1).f_code.co_filename),
                sys._getframe(1).f_code.co_name,
                sys._getframe(1).f_lineno,
                msg,
            )
        except:
            pass
        self.logger.error(msg)
        return

    def setlogger(
        self,
        level=LOG_LEVEL,
        open_console=OPEN_CONSOLE_LOG,
        open_file=OPEN_FILE_LOG,
        path=LOG_FILE_PATH,
    ):
        self.logger = _create_logger(level, open_console, open_file, path)


logger = Logger()


def creat_logger(
    level=LOG_LEVEL,
    open_console=OPEN_CONSOLE_LOG,
    open_file=OPEN_FILE_LOG,
    path=LOG_FILE_PATH,
):
    global logger
    logger.setlogger(level, open_console, open_file, path)
