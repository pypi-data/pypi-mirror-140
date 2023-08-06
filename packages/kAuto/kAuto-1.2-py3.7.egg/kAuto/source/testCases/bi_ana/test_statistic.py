import allure

from service.bi_ana.statistic_service import statistic_service


@allure.epic("bi分析")
@allure.story("车流统计")
class TestStatistic:
    @allure.title("车流统计")
    def test_traffic_statistic(self):
        statistic_service.traffic_statistic()
