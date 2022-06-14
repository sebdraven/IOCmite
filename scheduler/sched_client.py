
import imp
from redis import StrictRedis
from dateutil import parser
from datetime import datetime
import base64

from cti.cti_feeds import CTI_Feed
from suricata.suricata_dataset import Suricata_Dataset
from scheduler.last_run import LastRun

class Sched:
    def __init__(
        self,
        cti_feed: CTI_Feed,
        sc_dataset: Suricata_Dataset,
        is_redis=False,
        tmp_file="",
    ):
        self.client_redis = StrictRedis(db=1)
        self.cti_feed = cti_feed
        self.sc_dataset = sc_dataset
        self.last_run = LastRun(is_redis=is_redis, tmp_file=tmp_file)

    def run(self, attributes_datasets: dict):
        self.sc_dataset.connect()
        last_run = self.last_run.get_last_run()
        if last_run:
            date_from = parser.parse(last_run)
        else:
            date_from = None
        for type_attr, name_dataset_type in attributes_datasets.items():
            for att in self.cti_feed.get_last_attributes(date_from, type_attr):
                attr_encode = base64.b64encode(att["value"].encode()).decode()
                name_dataset = name_dataset_type["name"]
                type_suricata = name_dataset_type["type"]
                self.sc_dataset.add_dataset(name_dataset, type_suricata, attr_encode)
        self.sc_dataset.disconnect()
        time_run = datetime.now().isoformat()
        self.last_run.set_last_run(time_run)
