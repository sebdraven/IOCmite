import json
import logging
import re
import time
import tailer
from misp_client import MispClient
from multiprocessing import Process
import os.path
from redis import StrictRedis


class Alerts:
    def __init__(
        self,
        misp_client: MispClient,
        metadata: str,
        eve_json_file="",
        key_redis="suricata",
        db=0,
    ) -> None:
        self.misp_client = misp_client
        self.db = db
        self.key_redis = key_redis
        self.metadata = metadata
        self.eve_json_file = eve_json_file

    def pull(self, is_redis: bool, eve_json: bool):
        """Pull the alerts from the alerts suricata of the dataset and add a sighiting in MISP server
        Args:
            is_redis (bool): [True if the alerts are in redis]
            eve_json (bool): [True if the alerts are in eve_json]
        """

        if is_redis:
            self.__pull_redis()
        if eve_json:
            self.__pull_eve()

    def decode_message(self, message: str):
        """Decode a JSON message received from alerts suricata of the dataset
        and add a sighiting in MISP server

        Args:
            message ([strt]): [message of the alerts]
        """
        dict_message = json.loads(message)
        if (
            "alert" in dict_message
            and "metadata" in dict_message["alert"]
            and self.metadata in dict_message["alert"]["metadata"]
        ):
            if dict_message["app_proto"] == "http":
                hostname = dict_message["http"]["hostname"]
                self.misp_client.add_sighting(hostname)

    def __pull_redis(self):
        """Pull the alerts from the dataset of redis  and add a sighiting in MISP server"""

        client = StrictRedis(db=self.db)

        while True:
            if client.exists(self.key_redis):
                message = client.lpop(self.key_redis)
                if message:
                    dec = Process(target=self.decode_message, args=(message.decode(),))
                    dec.start()
            time.sleep(1)

    def __pull_eve(self):
        """Pull the alerts from the alerts suricata of the dataset and add a sighiting in MISP server"""
        if not os.path.isfile(self.eve_json_file):
            logging.error("%s is not file" % self.eve_json_file)
            return
        for line in tailer.follow(open(self.eve_json_file)):
            dec = Process(target=self.decode_message, args=(line,))
            dec.start()
        time.sleep(1)
