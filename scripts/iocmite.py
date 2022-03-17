#!/usr/bin/env python3
import argparse
import json
import logging
import os.path
from idstools import rule
from utils import logger
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


def check_metadata(settings: dict, logs: str):
    """Check if the metadata is valid.

    Args:
        settings (str): [file of the configuration]
    """
    rule_suricata = settings.get("rule", "")

    level = logging.getLevelName(logs)
    logger = Logger(level=level)

    if not os.path.isfile(rule_suricata):
        logger.log("[-] Suricata rule file is missing", level=level)
        return False
    rule_dict = {}
    try:
        rule_dict = rule.parse_file(rule_suricata)[0]
    except Exception as e:
        logger.log("[-] Suricata rule file is not valid", level=level)
        return False
    metadata_rule = rule_dict.get("metadata", {})
    metadata = settings.get("metadata", {})

    if metadata_rule and metadata:
        for m in metadata_rule:
            if metadata in m:
                return True
        else:
            return False


def sightings(settings: dict, is_redis: bool, eve_json: bool, log: str):
    """parse alerts Suricata in redis or eve_json to add sightings in MISP.

    Args:
        config (str): [file of the configuration]
        is_redis (bool): [if redis is used to store alerts]
        eve_json (bool): [if eve json is used to store alerts]
    """
    eve_json_file = ""
    level = logging.getLevelName(log)
    logger = Logger(level=level)
    logger.log("[-] Parse alerts to add sigthings in MISP", level=level)

    if eve_json:
        eve_json_file = settings["eve_json"]
        if not os.path.isfile(eve_json_file):
            logger.log("[-] Eve json file is missing", level=level)
            exit(1)

    mips_url = settings.get("misp", {}).get("url", "")
    misp_key = settings.get("misp", {}).get("key", "")

    if mips_url and misp_key:
        client_misp = MispClient(logger, mips_url, misp_key)
        alerts = Sightings(
            client_misp, settings["metadata"], logger, eve_json_file=eve_json_file
        )
        alerts.pull(is_redis, eve_json_file)
    else:
        logger.log("[-] MISP url or key is missing", level=level)
        exit(1)


def import_iocs(settings: dict, is_redis: bool, is_tmp_file: bool, log: str):
    """Download the last indicator from the the last run to store in a dataset Suricata.

    Args:
        setting (str): [file of the configuration]
        is_redis (str): [if redis is used to store the last run]
        tmp_file (str): [if a temorary file is used to store the last run]
    """
    level = logging.getLevelName(log)
    logger = Logger(level=level)
    logger.log("[-] Import IOCs in dataset Suricata", level=level)

    url_misp = settings.get("misp", {}).get("url", "")
    key_misp = settings.get("misp", {}).get("key", "")
    if url_misp and key_misp:
        client_misp = MispClient(logger, url_misp, key_misp)
        sc_dataset = Suricata_Dataset()

        if is_tmp_file:
            tmp_file = settings.get("tmp_file", "")
            logger.log("[-] tmp file {}".format(tmp_file), level=level)
            if tmp_file:
                sched_run = Sched(client_misp, sc_dataset, tmp_file=tmp_file)
        if is_redis:
            logger.log("[-] redis setup", level=level)
            sched_run = Sched(client_misp, sc_dataset, is_redis=True)
        datasets = settings.get("datasets", {}).get("sources", {}).get("misp", "")
        logger.log("[-] datasets {}".format(datasets), level=level)
        if datasets:
            sched_run.run(datasets)
        else:
            logger.log("[-] No dataset to import", level=level)
            exit(1)
    logger.log("[-] Import IOCs in dataset Suricata finished", level=level)


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
    settings = None

    if args.config:
        settings = config(args.config)
    else:
        print("[-] Configuration file is missing")
        return exit(1)

    metadata_is_valid = check_metadata(settings, args.log)
    if not metadata_is_valid:
        print("[-] Metadata is not set correctly")
        return exit(1)
    print("[+] Metadata is set correctly")
    print("[+] Start IOCmite")
    print("[+] settings: {}".format(settings))
    if args.import_ioc and settings:
        import_iocs(settings, args.redis, args.tmp_file, args.log)
    if args.sightings and args.config and settings:
        sightings(settings, args.redis, args.eve_json, args.log)


if __name__ == "__main__":
    main()
