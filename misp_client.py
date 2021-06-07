from pymisp.api import PyMISP


class MispClient:
    def __init__(self, url, key):

        self.api = PyMISP(url=url, key=key)

    def get_last_attributes(self, datefrom, type_attribute):
        res = self.api.search(
            controller="attributes",
            date_from=datefrom,
            to_ids=1,
            type_attribute=type_attribute,
        )
        if res:
            for r in res["Attribute"]:
                yield r
