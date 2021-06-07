import argparse
import json
from suricata_dataset import Suricata_Dataset
from misp_client import MispClient
from sched_client import Sched
import os.path


def run(config):
    if os.path.isfile(config):
        setting = json.load(open(config))
        client_misp = MispClient(setting["misp"]["url"], setting["misp"]["key"])
        sc_dataset = Suricata_Dataset()
        sched_run = Sched(client_misp, sc_dataset)
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

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_commande_line()
    if args.run and args.config:
        run(args.config)
        pass
