import allure

from service.report_center.sta_report_service import sta_report_service


@allure.epic("报表中心")
@allure.story("统计报表")
class TestStaReport:

    @allure.title("车场收入日报")
    def test_park_income_day(self):
        sta_report_service.park_income_day()

    @allure.title("车流统计日报")
    def test_park_traffic_day(self):
        sta_report_service.park_traffic_day()

    @allure.title("24小时剩余车位统计")
    def test_freeLot_sta(self):
        sta_report_service.freeLot_sta()
