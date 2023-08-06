import pytest

from service.login.login_service import login_service
from utils.read_config import read_config


@pytest.fixture(scope="session", autouse=True)
def login():
    group_info = read_config.read("group")
    login_service.login(group_info["username"], group_info["password"])

