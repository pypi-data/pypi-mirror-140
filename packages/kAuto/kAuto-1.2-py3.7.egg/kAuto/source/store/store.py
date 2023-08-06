import copy


class Store:
    groupId = ""
    request_headers = {}
    lotList = []

    def getter_request_headers(self):
        return copy.deepcopy(self.request_headers)

    def getter_lotList(self):
        return copy.deepcopy(self.lotList)


store = Store()
