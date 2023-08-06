"""
bi分析
车场报告
"""
from api.parking_hk_api import parking_hk_api
from store.store import store


class ParkReportService:
    # 月报
    def pageReport(self, year=None):
        if year is None:
            year = []
        return parking_hk_api.pageReport("", year)

    # 获取邮箱配置
    def getAllEmailConfig(self):
        groupId = store.groupId
        return parking_hk_api.getAllEmailConfig(groupId)

    # 月报详情
    def getMonthReportDetail(self, pid):
        parking_hk_api.getMonthReportDetail(pid)


park_report_service = ParkReportService()
