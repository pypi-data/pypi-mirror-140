from store.store import store
from utils.logger import log
from utils.read_config import read_config
from core.base_request import BaseRequest


class CloudRequest(BaseRequest):

    def request_http(self, data):
        domain = read_config.read("cloud")["domain"]
        data["url"] = domain + data["url"]

        if store.request_headers == {}:
            assert False, "请求头为空"
        data["headers"] = store.getter_request_headers()

        resp = super().request_http(data).json()
        log.info(f"resp: \n{resp}")
        assert resp["respCode"] == "200", f"接口 {data['url']} 返回失败"
        return resp


cloud_request = CloudRequest()
