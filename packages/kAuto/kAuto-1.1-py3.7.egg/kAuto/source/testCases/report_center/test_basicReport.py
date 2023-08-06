import allure

from service.report_center.basic_report_service import basic_report_service


@allure.epic("报表中心")
@allure.story("基础报表")
class TestBasicReport:

    @allure.title("车场管理表")
    def test_getParkingData(self):
        basic_report_service.getParkingData()

    @allure.title("车场管理表 详情")
    def test_getParkingData_detail(self):
        result = basic_report_service.getParkingData()["data"]["result"]
        if len(result) == 0:
            return
        basic_report_service.getParkingData_detail(result[0]["lotCode"])

    @allure.title("设备管理表")
    def test_getDeviceList(self):
        basic_report_service.getDeviceList()

    @allure.title("设备监控表")
    def test_deviceMonitor(self):
        basic_report_service.deviceMonitor()
