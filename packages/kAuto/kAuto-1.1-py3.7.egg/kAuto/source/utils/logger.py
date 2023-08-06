import sys
import logging
import time

from utils.dir_config import *
from utils.read_config import read_config


class Logger:
    """
    日志处理类
    """

    def __init__(self, path):
        """
        :param path: 日志路径
        """
        path = LOG_DIR + os.sep + ROOT_DIR.split(os.sep)[-1] + ".log"
        self._clean_log(path)
        level = self._read_level()
        path_list = path.split(".")
        name = path_list[0]
        # 格式化成2016-03-20 11:45:39形式
        now = time.strftime("%Y-%m-%d_%H_%M", time.localtime())
        name = name + "_" + now
        path = name + "." + path_list[1]

        # 创建一个日志器_logger并设置其日志级别为DEBUG
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        # 创建一个日志器_logger并设置其日志级别为DEBUG
        self._logger = logging.getLogger(path)
        self._logger.setLevel(level)

        # 创建一个格式器formatter并将其添加到处理器handler
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        handler.setFormatter(formatter)

        # 为日志器_logger添加上面创建的处理器handler
        self._logger.addHandler(handler)

        # 设置文件日志
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self._logger.addHandler(file_handler)

    def debug(self, message, *args, **kwargs):
        """
        :param message: debug信息
        :return:
        """
        self._logger.debug(message, *args, **kwargs)

    def info(self, message):
        """
        :param message: info信息
        :return:
        """
        self._logger.info(message)

    def error(self, massage):
        self._logger.error(massage)

    # 删除多余日志，只保留当天日志
    def _clean_log(self, path: str):
        name = path.split(".")[0].split(os.sep)[-1]
        files = os.listdir(LOG_DIR)
        now = time.strftime("%Y-%m-%d", time.localtime())
        for file in files:
            if file == "__init__.py":
                continue
            try:
                file_day = file.split(".")[0].split(f"{name}_")[1].split("_")[0]
                if file_day != now:
                    os.remove(os.path.join(LOG_DIR, file))
            except:
                pass

    def _read_level(self):
        read_level = read_config.read("log_level")
        if read_level == "debug":
            level = logging.DEBUG
        elif read_level == "info":
            level = logging.INFO
        elif read_level == "error":
            level = logging.ERROR
        else:
            level = logging.INFO
        return level


log = Logger(os.path.join(LOG_DIR))
