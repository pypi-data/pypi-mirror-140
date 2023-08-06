import allure

from service.bi_ana.parkReport_service import park_report_service


@allure.epic("bi分析")
@allure.story("车场报告")
class TestParkReport:

    @allure.title("月报查询")
    def test_pageReport(self):
        park_report_service.pageReport()

    @allure.title("邮箱配置查询")
    def test_getAllEmailConfig(self):
        park_report_service.getAllEmailConfig()

    @allure.title("月报详情")
    def test_getMonthReportDetail(self):
        data = park_report_service.pageReport()["data"]
        if data == "查询数据为空":
            return
        pid = data["records"][0]["pid"]
        park_report_service.getMonthReportDetail(pid)
