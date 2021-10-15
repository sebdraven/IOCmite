#!/usr/bin/env python3
import argparse
import json
import logging
import os.path
from utils.logger import Logger
from suricata_misp.suricata_dataset import Suricata_Dataset
from suricata_misp.misp_client import MispClient
from suricata_misp.sched_client import Sched
from suricata_misp.sightings import Sightings


def sightings(config: str, is_redis: bool, eve_json: bool, log: str):
    """parse alerts Suricata in redis or eve_json to add sightings in MISP.

    Args:
        config (str): [file of the configuration]
        is_redis (bool): [if redis is used to store alerts]
        eve_json (bool): [if eve json is used to store alerts]
    """
    eve_json_file = ""
    level = logging.getLevelName(log)
    logger = Logger(level=level)
    logger.log("[*] Parse alerts to add sigthings in MISP", level=level)
    if os.path.isfile(config):
        setting = json.load(open(config))
        if eve_json:
            eve_json_file = setting["eve_json"]
        client_misp = MispClient(logger, setting["misp"]["url"], setting["misp"]["key"])
        alerts = Sightings(
            client_misp, setting["metadata"], logger, eve_json_file=eve_json_file
        )
        alerts.pull(is_redis, eve_json)
    else:
        logger.log("%s is not a file" % config, level=logging.ERROR)


def import_iocs(config: str, is_redis: bool, tmp_file: bool, log: str):
    """Download the last indicator from the the last run to store in a dataset Suricata.

    Args:
        config (str): [file of the configuration]
        is_redis (str): [if redis is used to store the last run]
        tmp_file (str): [if a temorary file is used to store the last run]
    """
    level = logging.getLevelName(log)
    logger = Logger(level=level)
    logger.log("[*] Import IOCs in dataset Suricata", level=level)
    if os.path.isfile(config):
        setting = json.load(open(config))
        if 'misp' in setting['sources']:
            client_misp = MispClient(logger, setting["misp"]["url"], setting["misp"]["key"])
            sc_dataset = Suricata_Dataset()

            if tmp_file:
                sched_run = Sched(client_misp, sc_dataset, tmp_file=setting["tmp_file"])
            if is_redis:
                sched_run = Sched(client_misp, sc_dataset, is_redis=True)
            sched_run.run(setting["datasets"]["sources"]["misp"])
    else:
        logger.log("%s is not a file" % config, level=logging.ERROR)
    logger.log("[*] Import IOCs in dataset Suricata finished", level=level)


def parse_commande_line():
    parser = argparse.ArgumentParser(description="IOCmite")
    parser.add_argument(
        "--import",
        action="store_true",
        help="Import IOCs in dataset Suricata",
        dest="import_ioc",
    )

    parser.add_argument(
        "--config", help="Configuration for MISP and Datasets", dest="config"
    )
    parser.add_argument("--redis", action="store_true", dest="redis")

    parser.add_argument("--tmp_file", action="store_true", dest="tmp_file")

    parser.add_argument("--sightings", action="store_true", dest="sightings")
    parser.add_argument("--eve_json", action="store_true", dest="eve_json")
    parser.add_argument(
        "--log",
        help="Log level",
        dest="log",
        default="INFO",
        choices=["DEBUG", "INFO", "ERROR", "WARNING"],
    )
    return parser.parse_args()


def main():
    args = parse_commande_line()
    if args.import_ioc and args.config:
        import_iocs(args.config, args.redis, args.tmp_file, args.log)
    if args.sightings and args.config:
        sightings(args.config, args.redis, args.eve_json, args.log)


if __name__ == "__main__":
    main()
