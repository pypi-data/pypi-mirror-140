from store.store import store
from utils.logger import log
from utils.read_config import read_config
from core.base_request import BaseRequest


class GroupRequest(BaseRequest):
    pass_urls = [
        "api/login/"
    ]

    def request_http(self, data):
        domain = read_config.read("group")["domain"]
        data["url"] = domain + data["url"]

        data = self.interceptor(data)

        resp = super().request_http(data).json()
        log.info(f"resp: \n{resp}")
        assert resp["resultCode"] == 200, f"接口 {data['url']} 返回失败"
        return resp

    # 拦截请求
    def interceptor(self, data):
        # 添加token
        pass_urls = [
            "api/login/"
        ]
        if not self.url_in_pass_url(data["url"], pass_urls):
            if store.request_headers == {}:
                assert False, "请求头为空"
            data["headers"] = store.getter_request_headers()
        # 添加language
        lan_urls = [
            "/api/frontend/menu/getMenuListByGroup"
        ]
        if self.url_in_pass_url(data["url"], lan_urls):
            data["headers"]["language"] = "zh_cn"
        return data

    def url_in_pass_url(self, url, pass_urls):
        for pass_url in pass_urls:
            if pass_url in url:
                return True
        return False


group_request = GroupRequest()
