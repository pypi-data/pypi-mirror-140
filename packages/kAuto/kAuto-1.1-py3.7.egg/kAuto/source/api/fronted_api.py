from core.group_request import group_request


class FrontedApi:
    def getMenuListByGroup(self):
        data = {
            "method": "get",
            "url": "/api/frontend/menu/getMenuListByGroup"
        }
        return group_request.request_http(data)


fronted_api = FrontedApi()
