"""
bi分析
楼层车流统计
"""
from api.parking_hk_api import parking_hk_api
from store.store import store
from utils.generate import generate


class StatisticService:

    # 车流统计
    def traffic_statistic(self, timeSelect=0, beginTime="", endTime="", lotCode=""):
        """
        :param timeSelect: 日期类型
                0 按天
                1 按月
        :param beginTime:
        :param endTime:
        :param lotCode:
        :return:
        """
        if timeSelect == 0:
            if beginTime == "":
                beginTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0]
            if endTime == "":
                endTime = beginTime
        elif timeSelect == 1:
            if beginTime == "":
                beginTime = generate.generate_current_month()
            if endTime == "":
                endTime = generate.generate_current_month()
        if lotCode == "":
            lotCode = store.getter_lotList()[0]["lotId"]
        parking_hk_api.traffic_statistic(beginTime, endTime, lotCode, timeSelect)


statistic_service = StatisticService()
