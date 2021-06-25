from pymisp.api import PyMISP
from pymisp.mispevent import MISPSighting
import logging


class MispClient:
    def __init__(self, url: str, key: str):

        self.api = PyMISP(url=url, key=key)

    def get_last_attributes(self, datefrom: str, type_attribute: str):
        res = self.api.search(
            controller="attributes",
            date_from=datefrom,
            to_ids=1,
            type_attribute=type_attribute,
        )
        if res:
            for r in res["Attribute"]:
                yield r

    def add_sighting(self, attribute_value: str):
        res = self.api.search(controller="attributes", value=attribute_value)
        for attr in res["Attribute"]:
            sight = MISPSighting()
            sight.from_dict(uuid=attr["uuid"], source="IDS")
            self.api.add_sighting(sight)
            logging.warning("add sighting to %s" % attribute_value)
