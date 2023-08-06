"""
bi分析
车场分析
"""
from api.parking_data_api import parking_data_api
from utils.generate import generate


class ParkAnaService:
    # 车场实况
    def getParkingAnalysis(self, dateType="day", startTime="", endTime=""):
        """
        :param dateType: 日期类型
                day 日
                month 月
        :param startTime:
        :param endTime:
        :return:
        """
        if dateType == "day":
            if startTime == "":
                startTime = generate.generate_today()
            if endTime == "":
                endTime = startTime
            parking_data_api.getParkingAnalysisDataDay("", [0], startTime, endTime)
        elif dateType == "month":
            if startTime == "":
                startTime = generate.generate_current_month()
            if endTime == "":
                endTime = startTime
            parking_data_api.getParkingAnalysisDataMonth("", [0], startTime, endTime)

    # 收入分析
    def getIncomeData(self, dateType="day", startTime="", endTime=""):
        """
        :param dateType: 日期类型
                day 日
                month 月
        :param startTime:
        :param endTime:
        :return:
        """
        if dateType == "day":
            if startTime == "":
                startTime = generate.generate_today()
            if endTime == "":
                endTime = startTime
            parking_data_api.getIncomeDataDay("", [0], startTime, endTime)
        elif dateType == "month":
            if startTime == "":
                startTime = generate.generate_current_month()
            if endTime == "":
                endTime = startTime
            parking_data_api.getIncomeDataMonth("", [0], startTime, endTime)

    # 车流分析
    def traffic(self, dateType="day", startTime="", endTime=""):
        """
        :param dateType: 日期类型
                day 日
                month 月
        :param startTime:
        :param endTime:
        :return:
        """
        if dateType == "day":
            if startTime == "":
                startTime = generate.generate_today()
            if endTime == "":
                endTime = startTime
            parking_data_api.dayTraffic([0], startTime, endTime)
        elif dateType == "month":
            if startTime == "":
                startTime = generate.generate_current_month()
            if endTime == "":
                endTime = startTime
            parking_data_api.monthTraffic([0], startTime, endTime)

    # 车位统计分析
    def space(self, dateType="day", startTime="", endTime=""):
        """
        :param dateType: 日期类型
                day 日
                month 月
        :param startTime:
        :param endTime:
        :return:
        """
        if dateType == "day":
            if startTime == "":
                startTime = generate.generate_today()
            if endTime == "":
                endTime = startTime
            parking_data_api.daySpace([0], startTime, endTime)
        elif dateType == "month":
            if startTime == "":
                startTime = generate.generate_current_month()
            if endTime == "":
                endTime = startTime
            parking_data_api.monthSpace([0], startTime, endTime)

    # 停车时长分析
    def parkTime(self, dateType="day", startTime="", endTime=""):
        """
        :param dateType: 日期类型
                day 日
                month 月
        :param startTime:
        :param endTime:
        :return:
        """
        if dateType == "day":
            if startTime == "":
                startTime = generate.generate_today()
            if endTime == "":
                endTime = startTime
        elif dateType == "month":
            if startTime == "":
                startTime = generate.generate_current_month()
            if endTime == "":
                endTime = startTime
        parking_data_api.parkingTime(dateType, [0], startTime, endTime)
        parking_data_api.parkingTimeDistribute(dateType, [0], startTime, endTime)


park_ana_service = ParkAnaService()
