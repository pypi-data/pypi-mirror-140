"""
报表中心
统计报表
"""
from api.parking_data_api import parking_data_api
from utils.generate import generate


class StaReportService:
    # 车场收入日报
    def park_income_day(self, startTime="", endTime=""):
        if startTime == "":
            startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0] + " 00:00:00"
        if endTime == "":
            endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0] + " 23:59:59"
        lotCodes = [0]
        parking_data_api.getDailyIncome(lotCodes, startTime, endTime)
        parking_data_api.getDailyIncomeStatistics(lotCodes, startTime, endTime)

    # 车场车流收入日报
    def park_traffic_day(self, startTime="", endTime=""):
        if startTime == "":
            startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0] + " 00:00:00"
        if endTime == "":
            endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0] + " 23:59:59"
        lotCodes = [0]
        parking_data_api.getDailyTrafficFlow(lotCodes, startTime, endTime)
        parking_data_api.getDailyTrafficFlowStatistics(lotCodes, startTime, endTime)

    # 24小时剩余车位统计
    def freeLot_sta(self, startTime="", endTime=""):
        if startTime == "":
            startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0] + " 00:00:00"
        if endTime == "":
            endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0] + " 23:59:59"
        lotCodes = [0]
        parking_data_api.getFreeLotStatistics(lotCodes, startTime, endTime)


sta_report_service = StaReportService()
