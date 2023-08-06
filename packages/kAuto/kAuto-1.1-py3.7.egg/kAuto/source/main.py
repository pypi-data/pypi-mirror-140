import os

import pytest

if __name__ == '__main__':
    pytest.main(["-vs", "./testCases/", "--alluredir=./reports", "--clean-alluredir"])
    os.system('allure serve ./reports')
