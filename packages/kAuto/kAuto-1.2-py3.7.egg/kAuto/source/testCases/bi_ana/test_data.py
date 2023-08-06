import allure

from service.bi_ana.data_service import data_service


@allure.epic("bi分析")
@allure.story("数据服务")
class TestData:

    @allure.title("汇总表查询")
    def test_table_search(self):
        data_service.total_table_search()

    @allure.title("车场排名")
    def test_park_rank(self):
        data_service.park_rank()
