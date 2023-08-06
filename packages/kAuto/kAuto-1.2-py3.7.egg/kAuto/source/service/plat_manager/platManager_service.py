"""
平台管理
平台管理
"""
from api.group_api import group_api
from store.store import store


class PlatManagerService:
    # 用户查询
    def pageUser(self, name="", phone="", sort="", sortField=""):
        group_api.pageUser(store.groupId, name, phone, sort, sortField)

    # 组织机构查询
    def queryGroupLotByCurrentGroupId(self):
        group_api.queryGroupLotByCurrentGroupId(store.groupId, "", "")

    # 角色查询
    def pageRole(self):
        group_api.pageRole(store.groupId, "", "")

    # 操作日志
    def pageOperationLog(self, operator="", startTime="", endTime="", operationType="", operationModule="",
                         operationStatus="", currentGroup="", operationContent=""):
        group_api.pageOperationLog(operator, startTime, endTime, operationType, operationModule, operationStatus,
                                   currentGroup, operationContent)


plat_manager_service = PlatManagerService()
