import time

import requests
from retrying import retry

from utils.logger import log


class BaseRequest:
    @retry(stop_max_attempt_number=3)
    def request_http(self, data: dict):
        log.info(f"request:\n {data}")
        start = time.time()
        rep = requests.request(**data)
        end = time.time()
        log.debug(f"used time: {end - start}")
        return rep


base_request = BaseRequest()
