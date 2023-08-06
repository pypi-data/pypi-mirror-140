"""
报表中心
基础报表
"""
from api.parking_data_api import parking_data_api
from store.store import store


class BasicReportService:
    # 车场管理表
    def getParkingData(self, linkStatus="", parkType=""):
        lotCodes = [0]
        return parking_data_api.getParkingData(lotCodes, linkStatus, parkType)

    # 车场管理表 详情
    def getParkingData_detail(self, lotCode):
        parking_data_api.getSignalParkingDetail(lotCode)
        parking_data_api.threeLevelData()

    # 设备管理表
    def getDeviceList(self, deviceStatus=""):
        parking_data_api.getDeviceList([0], deviceStatus)

    # 设备监控表
    def deviceMonitor(self):
        lotList = store.getter_lotList()
        codes = []
        for lot in lotList:
            codes.append(lot["lotId"])
        parking_data_api.deviceMonitor(codes)


basic_report_service = BasicReportService()
