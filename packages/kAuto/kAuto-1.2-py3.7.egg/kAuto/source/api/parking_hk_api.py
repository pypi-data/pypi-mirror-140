from core.cloud_request import cloud_request


class ParkingHkApi:
    def getIncomeAnalysisData(self, dateType, startTime, endTime, lotCodes):
        data = {
            "method": "post",
            "url": "/parking-hk/home-page/getIncomeAnalysisData",
            "json": {
                "dateType": dateType,
                "endTime": endTime,
                "lotCodes": lotCodes,
                "startTime": startTime
            }
        }
        return cloud_request.request_http(data)

    def getAccuracyTurnoverRate(self, dateType, startTime, endTime, lotCodes):
        data = {
            "method": "post",
            "url": "/parking-hk/home-page/getAccuracyTurnoverRate",
            "json": {
                "dateType": dateType,
                "endTime": endTime,
                "lotCodes": lotCodes,
                "startTime": startTime
            }
        }
        return cloud_request.request_http(data)

    def trafficFlowData(self, firstMonth, secondMonth, groupId):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/aggregateData/trafficFlowData",
            "json": {
                "firstMonth": firstMonth,
                "secondMonth": secondMonth,
                "groupId": groupId
            }
        }
        return cloud_request.request_http(data)

    def paymentMethodNum(self, firstMonth, secondMonth, groupId):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/aggregateData/paymentMethodNum",
            "json": {
                "firstMonth": firstMonth,
                "secondMonth": secondMonth,
                "groupId": groupId
            }
        }
        return cloud_request.request_http(data)

    def paymentMethodMoney(self, firstMonth, secondMonth, groupId):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/aggregateData/paymentMethodMoney",
            "json": {
                "firstMonth": firstMonth,
                "secondMonth": secondMonth,
                "groupId": groupId
            }
        }
        return cloud_request.request_http(data)

    def payLocationNum(self, firstMonth, secondMonth, groupId):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/aggregateData/payLocationNum",
            "json": {
                "firstMonth": firstMonth,
                "secondMonth": secondMonth,
                "groupId": groupId
            }
        }
        return cloud_request.request_http(data)

    def fixChargePayMethod(self, firstMonth, secondMonth, groupId):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/aggregateData/fixChargePayMethod",
            "json": {
                "firstMonth": firstMonth,
                "secondMonth": secondMonth,
                "groupId": groupId
            }
        }
        return cloud_request.request_http(data)

    def accuracyRate(self, firstMonth, secondMonth, groupId):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/aggregateData/accuracyRate",
            "json": {
                "firstMonth": firstMonth,
                "secondMonth": secondMonth,
                "groupId": groupId
            }
        }
        return cloud_request.request_http(data)

    def traffic_statistic(self, beginTime, endTime, lotCode, timeSelect):
        data = {
            "method": "post",
            "url": "/parking-hk/floor/traffic/statistic",
            "json": {
                "beginTime": beginTime,
                "endTime": endTime,
                "lotCode": lotCode,
                "timeSelect": timeSelect
            }
        }
        return cloud_request.request_http(data)

    def pageReport(self, groupId, year):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/parkingReportNew/pageReport",
            "json": {
                "groupId": groupId,
                "pageNo": 1,
                "pageSize": 10,
                "year": year
            }
        }
        return cloud_request.request_http(data)

    def getAllEmailConfig(self, groupId):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/parkingReportNew/getAllEmailConfig",
            "params": {
                "groupId": groupId
            }
        }
        return cloud_request.request_http(data)

    def getMonthReportDetail(self, pid):
        data = {
            "method": "post",
            "url": "/parking-hk/hk/parkingReportNew/getMonthReportDetail",
            "params": {
                "pid": pid
            }
        }
        return cloud_request.request_http(data)


parking_hk_api = ParkingHkApi()
