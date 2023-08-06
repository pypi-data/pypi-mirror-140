import allure

from service.plat_manager.platManager_service import plat_manager_service


@allure.epic("平台管理")
@allure.story("平台管理")
class TestPlatManager:

    @allure.title("用户查询")
    def test_pageUser(self):
        plat_manager_service.pageUser()

    @allure.title("组织机构查询")
    def test_queryGroupLotByCurrentGroupId(self):
        plat_manager_service.queryGroupLotByCurrentGroupId()

    @allure.title("角色查询")
    def test_pageRoled(self):
        plat_manager_service.pageRole()

    @allure.title("操作日志")
    def test_pageOperationLog(self):
        plat_manager_service.pageOperationLog()
