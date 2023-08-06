from core.cloud_request import cloud_request


class ParkingDataApi:

    def getParkingTimeDistribute(self, dateType, startTime, endTime, lotCodes):
        data = {
            "method": "post",
            "url": "/parking-data/parkingOverView/getParkingTimeDistribute",
            "json": {
                "dateType": dateType,
                "endTime": endTime,
                "lotCodes": lotCodes,
                "startTime": startTime
            }
        }
        return cloud_request.request_http(data)

    def getTopFive(self, lotCodes, startTime, endTime, areaType, codes, dateType):
        data = {
            "method": "post",
            "url": "/parking-data/comparison/topFive/getTopFive",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime,
                "areaType": areaType,
                "codes": codes,
                "dateType": dateType
            }
        }
        return cloud_request.request_http(data)

    def getParkingAnalysisDataDay(self, organizationId, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/parkingAnalysis/getParkingAnalysisDataDay",
            "json": {
                "organizationId": organizationId,
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getParkingAnalysisDataMonth(self, organizationId, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/parkingAnalysis/getParkingAnalysisDataMonth",
            "json": {
                "organizationId": organizationId,
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getIncomeDataMonth(self, organizationId, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/incomeAnalysis/getIncomeDataMonth",
            "json": {
                "organizationId": organizationId,
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getIncomeDataDay(self, organizationId, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/incomeAnalysis/getIncomeDataDay",
            "json": {
                "organizationId": organizationId,
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def dayTraffic(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/yardAnalysis/dayTraffic",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def monthTraffic(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/yardAnalysis/monthTraffic",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def daySpace(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/yardAnalysis/daySpace",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def monthSpace(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/yardAnalysis/monthSpace",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def parkingTime(self, dateType, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/yardAnalysis/parkingTime",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime,
                "dateType": dateType
            }
        }
        return cloud_request.request_http(data)

    def parkingTimeDistribute(self, dateType, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/yardAnalysis/parkingTimeDistribute",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime,
                "dateType": dateType
            }
        }
        return cloud_request.request_http(data)

    def getDailyIncome(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/statisticalReport/getDailyIncome",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getDailyIncomeStatistics(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/statisticalReport/getDailyIncomeStatistics",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getDailyTrafficFlow(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/statisticalReport/getDailyTrafficFlow",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getDailyTrafficFlowStatistics(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/statisticalReport/getDailyTrafficFlowStatistics",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getFreeLotStatistics(self, lotCodes, startTime, endTime):
        data = {
            "method": "post",
            "url": "/parking-data/statisticalReport/getFreeLotStatistics",
            "json": {
                "lotCodes": lotCodes,
                "startTime": startTime,
                "endTime": endTime
            }
        }
        return cloud_request.request_http(data)

    def getInParkVehicleDetail(self, lotCodes, plateNumber, carType):
        data = {
            "method": "post",
            "url": "/parking-data/detailReport/getInParkVehicleDetail",
            "json": {
                "lotCodes": lotCodes,
                "plateNumber": plateNumber,
                "carType": carType,
                "pageNo": 1,
                "pageSize": 10
            }
        }
        return cloud_request.request_http(data)

    def getImageData(self, id, inOutType):
        data = {
            "method": "post",
            "url": "/parking-data/detailReport/getImageData",
            "json": {
                "id": id,
                "inOutType": inOutType
            }
        }
        return cloud_request.request_http(data)

    def getInOutDetail(self, lotCodes, plateNumber, carType, startTime, endTime, inOutType, releaseType):
        data = {
            "method": "post",
            "url": "/parking-data/detailReport/getInOutDetail",
            "json": {
                "lotCodes": lotCodes,
                "plateNumber": plateNumber,
                "carType": carType,
                "pageNo": 1,
                "pageSize": 10,
                "startTime": startTime,
                "endTime": endTime,
                "inOutType": inOutType,
                "releaseType": releaseType
            }
        }
        return cloud_request.request_http(data)

    def getTempIncomeDetail(self, lotCodes, plateNumber, startTime, endTime, payMethod, orderNo):
        data = {
            "method": "post",
            "url": "/parking-data/detailReport/getTempIncomeDetail",
            "json": {
                "lotCodes": lotCodes,
                "plateNumber": plateNumber,
                "pageNo": 1,
                "pageSize": 10,
                "startTime": startTime,
                "endTime": endTime,
                "payMethod": payMethod,
                "orderNo": orderNo
            }
        }
        return cloud_request.request_http(data)

    def getFixChargeDetail(self, lotCodes, startTime, endTime, payMethod, orderNo, fixCardName, rechargeType):
        data = {
            "method": "post",
            "url": "/parking-data/detailReport/getFixChargeDetail",
            "json": {
                "lotCodes": lotCodes,
                "pageNo": 1,
                "pageSize": 10,
                "startTime": startTime,
                "endTime": endTime,
                "payMethod": payMethod,
                "orderNo": orderNo,
                "fixCardName": fixCardName,
                "rechargeType": rechargeType
            }
        }
        return cloud_request.request_http(data)

    def getSellerChargeDetail(self, lotCodes, startTime, endTime, orderNo, rechargeType):
        data = {
            "method": "post",
            "url": "/parking-data/detailReport/getSellerChargeDetail",
            "json": {
                "lotCodes": lotCodes,
                "pageNo": 1,
                "pageSize": 10,
                "startTime": startTime,
                "endTime": endTime,
                "orderNo": orderNo,
                "rechargeType": rechargeType
            }
        }
        return cloud_request.request_http(data)

    def getLongStayReportData(self, lotCodes, carPlateNumber, carType, stayTime):
        data = {
            "method": "post",
            "url": "/parking-data/longStayReport/getLongStayReportData",
            "json": {
                "lotCodes": lotCodes,
                "carPlateNumber": carPlateNumber,
                "carType": carType,
                "pageNo": 1,
                "pageSize": 10,
                "stayTime": stayTime
            }
        }
        return cloud_request.request_http(data)

    def vehicleParkingDetail(self, lotCodes, outEndTime, outStartTime, inStartTime, inEndTime, carPlateNumber):
        data = {
            "method": "post",
            "url": "/parking-data/vehicleParkingDetail/queryList",
            "json": {
                "lotCodes": lotCodes,
                "outEndTime": outEndTime,
                "outStartTime": outStartTime,
                "inStartTime": inStartTime,
                "inEndTime": inEndTime,
                "carPlateNumber": carPlateNumber,
                "pageNum": 1,
                "pageSize": 10
            }
        }
        return cloud_request.request_http(data)

    def vehicleParkingDetail_queryDetail(self, entryId, lotCode):
        data = {
            "method": "post",
            "url": "/parking-data/vehicleParkingDetail/queryDetail",
            "json": {
                "entryId": entryId,
                "lotCode": lotCode
            }
        }
        return cloud_request.request_http(data)

    def getParkingData(self, lotCodes, linkStatus, parkType):
        data = {
            "method": "post",
            "url": "/parking-data/manageInfo/getParkingData",
            "json": {
                "lotCodes": lotCodes,
                "pageNo": 1,
                "pageSize": 10,
                "linkStatus": linkStatus,
                "parkType": parkType
            }
        }
        return cloud_request.request_http(data)

    def getSignalParkingDetail(self, lotCode):
        data = {
            "method": "post",
            "url": "/parking-data/manageInfo/getSignalParkingDetail",
            "json": {
                "lotCode": lotCode
            }
        }
        return cloud_request.request_http(data)

    def threeLevelData(self):
        data = {
            "method": "get",
            "url": "/parking-data/manageInfo/threeLevelData"
        }
        return cloud_request.request_http(data)

    def getDeviceList(self, lotCodes, deviceStatus):
        data = {
            "method": "post",
            "url": "/parking-data/manageInfo/getDeviceList",
            "json": {
                "lotCodes": lotCodes,
                "pageNum": 1,
                "pageSize": 10,
                "deviceStatus": deviceStatus
            }
        }
        return cloud_request.request_http(data)

    def deviceMonitor(self, lotCodes):
        data = {
            "method": "post",
            "url": "/parking-data/manageInfo/deviceMonitor",
            "json": {
                "lotCodes": lotCodes
            }
        }
        return cloud_request.request_http(data)


parking_data_api = ParkingDataApi()
