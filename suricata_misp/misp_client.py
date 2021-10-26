from pymisp.api import PyMISP
from pymisp.mispevent import MISPSighting
from utils.logger import Logger
import logging


class MispClient:
    def __init__(self, logger: Logger, url: str, key: str):

        self.api = PyMISP(url=url, key=key)
        self.logger = logger

    def get_last_attributes(self, datefrom: str, type_attribute: str):
        """Get last attributes from the device .

        Args:
            datefrom (str): [date from the last attributes]
            type_attribute (str): [atribute type of MISP]

        Yields:
            [str]: [values of the attributes ]
        """
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
        """Add a sight in MISP on the attribute value.

        Args:
            attribute_value (str): [attribut value to add sight]
        """
        res = self.api.search(controller="attributes", value=attribute_value)
        for attr in res["Attribute"]:
            event = self.api.get_event(attr["event_id"])
            sight = MISPSighting()
            sight.from_dict(uuid=attr["uuid"], source="IDS")
            self.api.add_sighting(sight)
            self.logger.log(
                "add sighting to %s from event %s title: %s"
                % (attribute_value, event["Event"]["id"], event["Event"]["info"]),
                level=self.logger.level,
            )
