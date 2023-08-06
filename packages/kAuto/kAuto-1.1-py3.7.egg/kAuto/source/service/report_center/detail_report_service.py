"""
报表中心
明细报表
"""
from api.parking_data_api import parking_data_api
from store.store import store
from utils.generate import generate


class DetailReportService:
    # 场内车辆明细
    def getInParkVehicleDetail(self, plateNumber="", carType=""):
        return parking_data_api.getInParkVehicleDetail([0], plateNumber, carType)

    # 场内车辆明细 预览
    def InParkVehicle_img(self, id, inOutType):
        parking_data_api.getImageData(id, inOutType)

    # 进出车辆明细
    def getInOutDetail(self, plateNumber="", carType="", startTime="", endTime="", inOutType="", releaseType=None):
        if startTime == "":
            startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0] + " 00:00:00"
        if endTime == "":
            endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0] + " 23:59:59"
        if releaseType is None:
            releaseType = []
        return parking_data_api.getInOutDetail([0], plateNumber, carType, startTime, endTime, inOutType, releaseType)

    # 进出车辆明细 预览
    def getInOutDetail_img(self, id, inOutType):
        parking_data_api.getImageData(id, inOutType)

    # 临停收费明细
    def getTempIncomeDetail(self, plateNumber="", startTime="", endTime="", payMethod="", orderNo=None):
        if startTime == "":
            startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0] + " 00:00:00"
        if endTime == "":
            endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0] + " 23:59:59"
        return parking_data_api.getTempIncomeDetail([0], plateNumber, startTime, endTime, payMethod, orderNo)

    # 固定车充值明细
    def getFixChargeDetail(self, startTime="", endTime="", payMethod="", orderNo=None, fixCardName=None,
                           rechargeType=""):
        if startTime == "":
            startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0] + " 00:00:00"
        if endTime == "":
            endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0] + " 23:59:59"
        return parking_data_api.getFixChargeDetail([0], startTime, endTime, payMethod, orderNo, fixCardName,
                                                   rechargeType)

    # 商家充值明细
    def getSellerChargeDetail(self, startTime="", endTime="", orderNo=None, rechargeType=""):
        if startTime == "":
            startTime = generate.just_time(generate.generate_localTime(), days=-6).split(" ")[0] + " 00:00:00"
        if endTime == "":
            endTime = generate.just_time(generate.generate_localTime(), days=-1).split(" ")[0] + " 23:59:59"
        parking_data_api.getSellerChargeDetail([0], startTime, endTime, orderNo, rechargeType)

    # 停留过长车辆明细
    def getLongStayReportData(self, carPlateNumber="", carType="", stayTime=""):
        return parking_data_api.getLongStayReportData([0], carPlateNumber, carType, stayTime)

    # 停留过长车辆明细 预览
    def getLongStayReportData_img(self, id, inOutType):
        parking_data_api.getImageData(id, inOutType)

    # 车辆停车明细
    def vehicleParkingDetail(self, outEndTime="", outStartTime="", inStartTime="", inEndTime="", carPlateNumber=""):
        lotList = store.getter_lotList()
        codes = []
        for lot in lotList:
            codes.append(lot["lotId"])
        if outEndTime == "" and outStartTime == "" and inStartTime == "" and inEndTime == "":
            inStartTime = generate.generate_today()
            inEndTime = generate.generate_today()
        return parking_data_api.vehicleParkingDetail(codes, outEndTime, outStartTime, inStartTime, inEndTime,
                                                     carPlateNumber)

    # 车辆停车明细 查看详情
    def vehicleParkingDetail_detail(self, entryId, lotCode):
        data: dict = parking_data_api.vehicleParkingDetail_queryDetail(entryId, lotCode)["data"]
        if data.get("inId") is not None:
            parking_data_api.getImageData(data.get("inId"), 0)
        if data.get("outId") is not None:
            parking_data_api.getImageData(data.get("outId"), 1)


detail_report_service = DetailReportService()
