from api.fronted_api import fronted_api
from api.group_api import group_api
from api.login_api import login_api
from store.store import store


class LoginService:
    def login(self, phone, password):
        code = login_api.getImgCode()["data"]["imgCode"]
        login_info = login_api.login(phone, password, code)
        # 设置token
        store.request_headers["token"] = login_info["data"]["token"]
        # 设置lotList
        menuList = fronted_api.getMenuListByGroup()["data"]
        lotList = group_api.getAllGroupAndTreeList(menuList[0]["menuId"])["data"]["lotList"]
        store.lotList = lotList
        # 设置groupId
        groupId = login_api.getUserGroupList()["data"][0]["groupId"]
        store.request_headers["groupid"] = groupId
        store.groupId = groupId


login_service = LoginService()
