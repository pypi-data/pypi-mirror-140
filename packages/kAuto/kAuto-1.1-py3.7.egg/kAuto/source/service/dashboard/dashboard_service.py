"""
首页
"""
from api.parking_data_api import parking_data_api
from api.parking_hk_api import parking_hk_api
from utils.generate import generate


class DashBoardService:
    # 首页查询
    def search(self, dateType="month", startTime="", endTime=""):
        """
        :param dateType:
                    month 月
                    day 日
        :return:
        """
        if dateType == "month":
            if startTime == "":
                startTime = generate.generate_current_month_first_day()
            if endTime == "":
                endTime = generate.generate_today()
        elif dateType == "day":
            if startTime == "":
                startTime = generate.generate_today()
            if endTime == "":
                endTime = startTime
        lotCodes = [0]
        parking_hk_api.getIncomeAnalysisData(dateType, startTime, endTime, lotCodes)
        parking_hk_api.getAccuracyTurnoverRate(dateType, startTime, endTime, lotCodes)
        parking_data_api.getParkingTimeDistribute(dateType, startTime, endTime, lotCodes)


dashboard_service = DashBoardService()
