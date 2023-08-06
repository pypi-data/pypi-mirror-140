"""
bi分析
数据服务
"""
from api.parking_data_api import parking_data_api
from api.parking_hk_api import parking_hk_api
from store.store import store
from utils.generate import generate


class DataService:
    # 汇总表查询
    def total_table_search(self, firstMonth="", secondMonth=""):
        if firstMonth == "":
            firstMonth = generate.generate_current_month()
        if secondMonth == "":
            secondMonth = generate.generate_current_month()
        parking_hk_api.trafficFlowData(firstMonth, secondMonth, "")
        parking_hk_api.paymentMethodNum(firstMonth, secondMonth, "")
        parking_hk_api.paymentMethodMoney(firstMonth, secondMonth, "")
        parking_hk_api.payLocationNum(firstMonth, secondMonth, "")
        parking_hk_api.fixChargePayMethod(firstMonth, secondMonth, "")
        parking_hk_api.accuracyRate(firstMonth, secondMonth, "")

    # 车场排名
    def park_rank(self, dateType="day", startTime="", endTime=""):
        """
        :param dateType: 日期类型
                day
                month
        :param startTime:
        :param endTime:
        :return:
        """
        lotCodes = [0]
        if dateType == "day":
            if startTime == "":
                startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0]
            if endTime == "":
                endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0]
        elif dateType == "month":
            if startTime == "":
                startTime = generate.generate_current_month()
            if endTime == "":
                endTime = startTime
        areaType = "lot"
        lotList = store.getter_lotList()
        codes = []
        for lot in lotList:
            codes.append(lot["lotId"])
        parking_data_api.getTopFive(lotCodes, startTime, endTime, areaType, codes, dateType)


data_service = DataService()
