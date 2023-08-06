from core.group_request import group_request


class LoginApi:
    def getImgCode(self):
        data = {
            "method": "get",
            "url": "/api/login/getImgCode"
        }
        return group_request.request_http(data)

    def login(self, phone, password, code):
        data = {
            "method": "post",
            "url": "/api/login/login",
            "json": {
                "phone": phone,
                "password": password,
                "code": code
            }
        }
        return group_request.request_http(data)

    def getUserGroupList(self):
        data = {
            "method": "get",
            "url": "/api/group/user/getUserGroupList",
        }
        return group_request.request_http(data)


login_api = LoginApi()
