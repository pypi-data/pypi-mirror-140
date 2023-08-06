import allure
import pytest

from service.bi_ana.parkAna_service import park_ana_service


@allure.epic("bi分析")
@allure.story("车场分析")
class TestParkAna:
    parkAna_data_list = [
        {"dateType": "day"},
        {"dateType": "month"},
    ]

    @allure.title("车场实况")
    @pytest.mark.parametrize("parkAna_data", parkAna_data_list)
    def test_getParkingAnalysis(self, parkAna_data):
        park_ana_service.getParkingAnalysis(dateType=parkAna_data["dateType"])

    @allure.title("收入分析")
    @pytest.mark.parametrize("parkAna_data", parkAna_data_list)
    def test_getIncomeData(self, parkAna_data):
        park_ana_service.getIncomeData(dateType=parkAna_data["dateType"])

    @allure.title("车流分析")
    @pytest.mark.parametrize("parkAna_data", parkAna_data_list)
    def test_traffic(self, parkAna_data):
        park_ana_service.traffic(dateType=parkAna_data["dateType"])

    @allure.title("车位统计分析")
    @pytest.mark.parametrize("parkAna_data", parkAna_data_list)
    def test_traffic(self, parkAna_data):
        park_ana_service.space(dateType=parkAna_data["dateType"])

    @allure.title("停车时长分析")
    @pytest.mark.parametrize("parkAna_data", parkAna_data_list)
    def test_traffic(self, parkAna_data):
        park_ana_service.parkTime(dateType=parkAna_data["dateType"])
