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

def config(config: str):
    """Check if the configuration file is valid.

    Args:
        config (str): [file of the configuration]
    """
    if os.path.isfile(config):
        return json.load(open(config))
    else:
        return False

def sightings(config: dict, is_redis: bool, eve_json: bool, log: str):
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

    if eve_json:
        eve_json_file = config["eve_json"]
    client_misp = MispClient(logger, config["misp"]["url"], config["misp"]["key"])
    alerts = Sightings(
        client_misp, config["metadata"], logger, eve_json_file=eve_json_file
    )
    alerts.pull(is_redis, eve_json)
 

def import_iocs(setting: dict, is_redis: bool, is_tmp_file: bool, log: str):
    """Download the last indicator from the the last run to store in a dataset Suricata.

    Args:
        setting (str): [file of the configuration]
        is_redis (str): [if redis is used to store the last run]
        tmp_file (str): [if a temorary file is used to store the last run]
    """
    level = logging.getLevelName(log)
    logger = Logger(level=level)
    logger.log("[*] Import IOCs in dataset Suricata", level=level)

    
    url_misp = setting.get("misp", {}).get("url", "")
    key_misp = setting.get("misp", {}).get("key", "")
    if url_misp and key_misp:
        client_misp = MispClient(logger, url_misp, key_misp)
        sc_dataset = Suricata_Dataset()
        
        if is_tmp_file:
            tmp_file = setting.get("tmp_file", "")
            if tmp_file:
                sched_run = Sched(client_misp, sc_dataset, tmp_file=tmp_file)
        if is_redis:
            sched_run = Sched(client_misp, sc_dataset, is_redis=True)
        datasets = setting.get("sources", {}).get("misp", {}).get("datasets", "")
        if datasets:
            sched_run.run(datasets)
        else:
            logger.log("[-] No dataset to import", level=level)
            exit(1)    
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
    setting = None
    if args.config:
        setting = config(args.config)
    else:
        print("[-] Configuration file is missing")
        return exit(1)

    if args.import_ioc:
        import_iocs(setting, args.redis, args.tmp_file, args.log)
    if args.sightings and args.config:
        sightings(setting, args.redis, args.eve_json, args.log)


if __name__ == "__main__":
    main()
