from core.group_request import group_request


class GroupApi:
    def getAllGroupAndTreeList(self, menuId):
        data = {
            "method": "post",
            "url": "/api/group/lot/getAllGroupAndTreeList",
            "json": {
                "menuId": menuId
            }
        }
        return group_request.request_http(data)

    def pageUser(self, groupId, name, phone, sort, sortField):
        data = {
            "method": "post",
            "url": "/api/group/user/pageUser",
            "json": {
                "groupId": groupId,
                "name": name,
                "phone": phone,
                "pageNo": 1,
                "pageSize": 10,
                "sort": sort,
                "sortField": sortField
            }
        }
        return group_request.request_http(data)

    def queryGroupLotByCurrentGroupId(self, groupId, sort, sortField):
        data = {
            "method": "post",
            "url": "/api/group/lot/queryGroupLotByCurrentGroupId",
            "json": {
                "groupId": groupId,
                "pageNo": 1,
                "pageSize": 10,
                "sort": sort,
                "sortField": sortField
            }
        }
        return group_request.request_http(data)

    def pageRole(self, groupId, sort, sortField):
        data = {
            "method": "post",
            "url": "/api/role/pageRole",
            "json": {
                "groupId": groupId,
                "pageNo": 1,
                "pageSize": 10,
                "sort": sort,
                "sortField": sortField
            }
        }
        return group_request.request_http(data)

    def pageOperationLog(self, operator, startTime, endTime, operationType, operationModule, operationStatus,
                         currentGroup, operationContent):
        data = {
            "method": "post",
            "url": "/api/log/pageOperationLog",
            "json": {
                "operator": operator,
                "startTime": startTime,
                "endTime": endTime,
                "operationType": operationType,
                "operationModule": operationModule,
                "operationStatus": operationStatus,
                "currentGroup": currentGroup,
                "operationContent": operationContent,
                "pageNo": 1,
                "pageSize": 10
            }
        }
        return group_request.request_http(data)


group_api = GroupApi()
