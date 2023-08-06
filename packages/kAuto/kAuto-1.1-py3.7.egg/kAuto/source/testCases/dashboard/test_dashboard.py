import allure
import pytest

from service.dashboard.dashboard_service import dashboard_service


@allure.epic("首页")
@allure.story("首页")
class TestDashboard:
    search_data_list = [
        {"dateType": "month"},
        {"dateType": "day"}
    ]

    @allure.title("首页查询")
    @pytest.mark.parametrize("search_data", search_data_list)
    def test_search(self, search_data):
        dashboard_service.search(dateType=search_data["dateType"])
