import argparse
import json
import os.path
from suricata_dataset import Suricata_Dataset
from misp_client import MispClient
from sched_client import Sched
from alerts import Alerts


def alerts(config: str, is_redis: bool, eve_json: bool):
    if os.path.isfile(config):
        setting = json.load(open(config))
        if eve_json:
            eve_json_file = config["eve_json"]
        client_misp = MispClient(setting["misp"]["url"], setting["misp"]["key"])
        alerts = Alerts(client_misp, setting["metadata"])
        alerts.pull(is_redis, eve_json)


def run(config: str, is_redis: str, tmp_file: str):
    if os.path.isfile(config):
        setting = json.load(open(config))
        client_misp = MispClient(setting["misp"]["url"], setting["misp"]["key"])
        sc_dataset = Suricata_Dataset()
        sched_run = Sched(client_misp, sc_dataset, is_redis, tmp_file)
        sched_run.run(setting["datasets"])


def parse_commande_line():
    parser = argparse.ArgumentParser(description="Misp to Suricata")
    parser.add_argument(
        "--run",
        action="store_true",
        help="First import IOCs in dataset Suricata",
        dest="run",
    )

    parser.add_argument(
        "--config", help="Configuration for MISP and Datasets", dest="config"
    )
    parser.add_argument("--redis", action="store_true", dest="redis")

    parser.add_argument("--tmp_file", action="store_true", dest="tmp_file")

    parser.add_argument("--alerts", action="store_true", dest="alerts")
    parser.add_argument("--eve_json", action="store_true", dest="eve_json")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_commande_line()
    if args.run and args.config:
        run(args.config, args.redis, args.tmp_file)
    if args.alerts and args.config:
        alerts(args.config, args.redis, args.eve_json)
