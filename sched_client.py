from redis import StrictRedis
from dateutil import parser
from datetime import datetime
import base64


class Sched:
    def __init__(self, client_misp, sc_dataset):
        self.client_redis = StrictRedis(db=1)
        self.client_misp = client_misp
        self.sc_dataset = sc_dataset

    def run(self, attributes_datasets):
        self.sc_dataset.connect()
        last_run = self.client_redis.get("last_run")
        if last_run:
            date_from = parser.parse(last_run)
        else:
            date_from = None
        for type_attr, name_dataset_type in attributes_datasets.items():
            for att in self.client_misp.get_last_attributes(date_from, type_attr):
                attr_encode = base64.b64encode(att["value"].encode()).decode()
                name_dataset = name_dataset_type["name"]
                type_suricata = name_dataset_type["type"]
                self.sc_dataset.add_dataset(name_dataset, type_suricata, attr_encode)
        self.sc_dataset.disconnect()
        time_run = datetime.now().isoformat()
        self.client_redis.set("last_run", time_run)
