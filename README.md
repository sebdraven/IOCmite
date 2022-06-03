# Suricata from to sources CTI

[![Total alerts](https://img.shields.io/lgtm/alerts/g/sebdraven/IOCmite.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/sebdraven/IOCmite/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/sebdraven/IOCmite.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/sebdraven/IOCmite/context:python)

the purpose of the application is to import attributes from different sources of threat Intelligence into suricata datasets to put them under surveillance.

## Concepts of datasets in Suricata

Indicators can be saved in a suricata dataset and create detection rules on this dataset.

This concept is detailed [here](https://suricata.readthedocs.io/en/suricata-6.0.0/rules/datasets.html).

## Installation

```bash
git clone  https://github.com/sebdraven/iocmite.git
python3 -m'venv' venv && source venv\bin\activate
pip install -r requirements.txt`
python setup.py install
```

or

```bash
python -m'venv' venv && source venv\bin\activate
pip install iocmite
iocmite --help
```

Download the last release of Suricata [here](https://www.openinfosecfoundation.org/download/suricata-current.tar.gz)
and run:

```bash
tar xvfz suricata-6.0.x && cd suricata-6.0.x/python && python setup install
```

## Json setting and Rule Suricata for MISP source and Sightings

```JSON
{
    "misp": {
        "url": "",
        "key": ""
    },
    "eve_json": "/var/log/suricata/eve.json",
    "metadata": "sightings",
    "tmp_file": "/tmp/last_run",
    "rule": "",
    "datasets": {
        "sources": {
            "misp": {
                "ip-src": {
                    "name": "ips",
                    "type": "string"
                },
                "ip-dst": {
                    "name": "ips",
                    "type": "string"
                },
                "hostname": {
                    "name": "dbl",
                    "type": "string"
                },
                "domain": {
                    "name": "dbl",
                    "type": "string"
                },
                "user-agent": {
                    "name": "uabl",
                    "type": "string"
                }
                
            }
        }
    }
}
```

Sample signatures are provided in the rules directory. For example, the one matchine on HTTP hostname is:

```
alert http any any -> any any (msg: "domains TA (HTTP)"; http.host; dataset:isset,dbl, type string, state /var/lib/suricata/data/dbl.lst; sid:1100001; rev:1; metadata:sightings http.hostname;)
```

The metadata term in the rule suricata is the same in the setting JSON file. The signatures suppose a standard system wide Suricata installation, you will need to change the path in the `state`
option in the `dataset` keyword if ever you don't have a standard installation.

Setup the url and key of MISP in the json file.

## Usage

### Principles

To synchronize the IOCs in MISP with Suricata datasets, you need to run an import command periodically.
You can use a cron task to do so.

To send sightings back to MISP, you need to run a IOCmite instance that will wait for new events
and publish sightings as soon as they came.

### Example commands

To import indicators from MISP to suricata with redis to store last run time, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --import --redis
```

To import indicators from MISP to suricata with temp file to store last run time, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --import --tmp_file
```

To catch alert from redis and send sightings to MISP, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --redis --sightings
```

To catch alert from eve_json and send sightings to MISP, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --eve_json --sightings
```
