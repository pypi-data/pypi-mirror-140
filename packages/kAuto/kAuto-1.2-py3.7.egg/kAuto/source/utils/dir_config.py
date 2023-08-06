import os

# 项目根路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# case路径
CASE_DIR = os.path.join(ROOT_DIR, "testCases")
# utils路径
UTILS_DIR = os.path.join(ROOT_DIR, "utils")
# log目录
LOG_DIR = os.path.join(ROOT_DIR, "logs")
# 测试报告目录
REPORT_DIR = os.path.join(ROOT_DIR, "reports")
# global_config
GLOBAL_CONFIG = os.path.join(ROOT_DIR, "config.yml")
# stg配置文件
CONFIG_TEST_FILE = os.path.join(ROOT_DIR, "config_test.yml")
# prod配置文件
CONFIG_PROD_FILE = os.path.join(ROOT_DIR, "config_prod.yml")
