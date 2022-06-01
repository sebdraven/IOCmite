#!/usr/bin/env python3
import argparse
import json
import logging
import os.path
from idstools import rule
from utils.logger import get_logger
from suricata_misp.suricata_dataset import Suricata_Dataset
from suricata_misp.misp_client import MispClient
from suricata_misp.sched_client import Sched
from suricata_misp.sightings import Sightings
from logging import Logger


def config(config: str):
    """Check if the configuration file is valid.

    Args:
        config (str): [file of the configuration]
    """
    if os.path.isfile(config):
        return json.load(open(config))
    else:
        return False


def check_metadata(settings: dict, log: Logger):
    """Check if the metadata is valid.

    Args:
        settings (str): [file of the configuration]
    """
    rule_suricata = settings.get("rule", "")
    log.info("[-] Rule Suricata {}".format(rule_suricata))
    if not os.path.isfile(rule_suricata):
        log.error("[-] Suricata rule file is missing")
        return False
    rule_dict = {}
    try:
        rules = rule.parse_file(rule_suricata)
    except Exception as e:
        log.error("[-] Suricata rule file is not valid {}".format(e))
        return False

    for r in rules:
        metadata_rule = r.get("metadata", {})
        metadata = settings.get("metadata", {})

        if metadata_rule and metadata:
            for m in metadata_rule:
                if metadata not in m:
                    return False
    return True


def sightings(settings: dict, is_redis: bool, eve_json: bool, log: Logger):
    """parse alerts Suricata in redis or eve_json to add sightings in MISP.

    Args:
        config (str): [file of the configuration]
        is_redis (bool): [if redis is used to store alerts]
        eve_json (bool): [if eve json is used to store alerts]
    """
    eve_json_file = ""

    log.info("[-] Parse alerts to add sigthings in MISP")

    if eve_json:
        eve_json_file = settings["eve_json"]
        if not os.path.isfile(eve_json_file):
            log.error("[-] Eve json file is missing")
            exit(1)

    mips_url = settings.get("misp", {}).get("url", "")
    misp_key = settings.get("misp", {}).get("key", "")

    if mips_url and misp_key:
        client_misp = MispClient(log, mips_url, misp_key)
        alerts = Sightings(
            client_misp, settings["metadata"], log, eve_json_file=eve_json_file
        )
        alerts.pull(is_redis, eve_json_file)
    else:
        log.error("[-] MISP url or key is missing")
        exit(1)


def import_iocs(settings: dict, is_redis: bool, is_tmp_file: bool, log: Logger):
    """Download the last indicator from the the last run to store in a dataset Suricata.

    Args:
        setting (str): [file of the configuration]
        is_redis (str): [if redis is used to store the last run]
        tmp_file (str): [if a temorary file is used to store the last run]
    """

    log.info("[-] Import IOCs in dataset Suricata")

    url_misp = settings.get("misp", {}).get("url", "")
    key_misp = settings.get("misp", {}).get("key", "")
    if url_misp and key_misp:
        client_misp = MispClient(log, url_misp, key_misp)
        suri_socket = settings.get("suricata_socket", "/var/run/suricata/suricata-command.socket")
        sc_dataset = Suricata_Dataset(path_socket=suri_socket)

        if is_tmp_file:
            tmp_file = settings.get("tmp_file", "")
            log.info("[-] tmp file {}".format(tmp_file))
            if tmp_file:
                sched_run = Sched(client_misp, sc_dataset, tmp_file=tmp_file)
        if is_redis:
            log.info("[-] redis setup")
            sched_run = Sched(client_misp, sc_dataset, is_redis=True)
        datasets = settings.get("datasets", {}).get("sources", {}).get("misp", "")
        log.info("[-] datasets {}".format(datasets))
        if datasets:
            sched_run.run(datasets)
        else:
            log.info("[-] No dataset to import")
            exit(1)
    log.info("[-] Import IOCs in dataset Suricata finished")


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

    logger = get_logger(args.log)
    if args.config:
        settings = config(args.config)
    else:
        logger.error("[-] Configuration file is missing")
        return exit(1)
    metadata_is_valid = check_metadata(settings, logger)
    if not metadata_is_valid:
        logger.error("[-] Metadata is not set correctly")
        return exit(1)
    logger.debug("[+] Metadata is set correctly")
    logger.info("[+] Start IOCmite")
    if args.import_ioc:
        import_iocs(settings, args.redis, args.tmp_file, logger)
    if args.sightings:
        sightings(settings, args.redis, args.eve_json, logger)
    if args.import_ioc and settings:
        import_iocs(settings, args.redis, args.tmp_file, logger)
    if args.sightings and args.config and settings:
        sightings(settings, args.redis, args.eve_json, logger)


if __name__ == "__main__":
    main()
