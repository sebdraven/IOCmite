import json
import time
from misp_client import MispClient
from multiprocessing import Process
from redis import StrictRedis


class Alerts:
    def __init__(
        self, misp_client: MispClient, metadata: str, key_redis="suricata", db=0
    ) -> None:
        self.misp_client = misp_client
        self.db = db
        self.key_redis = key_redis
        self.metadata = metadata

    def pull(self, is_redis, eve_json):
        if is_redis:
            self.__pull_redis()
        if eve_json:
            self.__pull_eve()

    def decode_message(self, message):
        dict_message = json.loads(message.decode())
        if (
            "alert" in dict_message
            and "metadata" in dict_message["alert"]
            and self.metadata in dict_message["alert"]["metadata"]
        ):
            if dict_message["app_proto"] == "http":
                hostname = dict_message["http"]["hostname"]
                self.misp_client.add_sighting(hostname)

    def __pull_redis(self):
        client = StrictRedis(db=self.db)

        while True:
            if client.exists(self.key_redis):
                message = client.lpop(self.key_redis)
                if message:
                    dec = Process(target=self.decode_message, args=(message,))
                    dec.start()
            time.sleep(1)
