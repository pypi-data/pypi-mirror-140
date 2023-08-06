import allure

from service.report_center.detail_report_service import detail_report_service


@allure.epic("报表中心")
@allure.story("明细报表")
class TestStaReport:

    @allure.title("场内车辆明细")
    def test_getInParkVehicleDetail(self):
        detail_report_service.getInParkVehicleDetail()

    @allure.title("场内车辆明细 预览")
    def test_InParkVehicle_img(self):
        result = detail_report_service.getInParkVehicleDetail()["data"]["result"]
        if len(result) == 0:
            return
        car = result[0]
        detail_report_service.InParkVehicle_img(car["id"], "0")

    @allure.title("进出车辆明细")
    def test_getInOutDetail(self):
        detail_report_service.getInOutDetail()

    @allure.title("进出车辆明细 预览")
    def test_getInOutDetail_img(self):
        result = detail_report_service.getInOutDetail()["data"]["result"]
        if len(result) == 0:
            return
        car = result[0]
        detail_report_service.getInOutDetail_img(car["id"], car["inOutType"])

    @allure.title("临停收费明细")
    def test_getTempIncomeDetail(self):
        detail_report_service.getTempIncomeDetail()

    @allure.title("固定车充值明细")
    def test_getFixChargeDetail(self):
        detail_report_service.getFixChargeDetail()

    @allure.title("商家充值明细")
    def test_getSellerChargeDetail(self):
        detail_report_service.getSellerChargeDetail()

    @allure.title("停留过长车辆明细")
    def test_getLongStayReportData(self):
        detail_report_service.getLongStayReportData()

    @allure.title("停留过长车辆明细 预览")
    def test_getLongStayReportData_img(self):
        result = detail_report_service.getLongStayReportData()["data"]["result"]
        if len(result) == 0:
            return
        car = result[0]
        detail_report_service.getLongStayReportData_img(car["comeDetailId"], "0")

    @allure.title("车辆停车明细")
    def test_vehicleParkingDetail(self):
        detail_report_service.vehicleParkingDetail()

    @allure.title("车辆停车明细 查看详情")
    def test_vehicleParkingDetail_detail(self):
        result = detail_report_service.vehicleParkingDetail()["data"]["data"]
        if len(result) == 0:
            return
        car = result[0]
        detail_report_service.vehicleParkingDetail_detail(car["entryId"], car["lotCode"])
