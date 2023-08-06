import yaml

from utils.dir_config import *


class ReadConfig:
    # 获取配置文件属性值
    def read(self, param) -> str:
        ret = self._for_config(param, GLOBAL_CONFIG)
        if ret != "":
            return ret
        env = self._for_config("env", GLOBAL_CONFIG)
        if env == "test":
            return self._for_config(param, CONFIG_TEST_FILE)
        if env == "prod":
            return self._for_config(param, CONFIG_PROD_FILE)

    def _for_config(self, param, file):
        config = yaml.safe_load(open(file, encoding="utf-8"))
        if config is None:
            return ""
        for k, v in config.items():
            if param == k:
                return v
        return ""


read_config = ReadConfig()
