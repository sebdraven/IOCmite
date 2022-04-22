# Suricata from to sources CTI

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
        "datasets": {
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
        }
  }
}
```


```
alert http any any -> any any (msg: "domains TA"; http.host; dataset:isset,dbl; sid:234;threshold: type threshold, track by_rule, count 1, seconds 1 ;rev:1; metadata:sightings http.hostname;)
```

The metadata term in the rule suricata is the same in the setting JSON file.

Setup the url and key of MISP in the json file.

## Usage

To import indicators from MISP to suricata with redis to store last run time, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --run --redis
```

To import indicators from MISP to suricata with temp file to store last run time, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --run --tmp_file
```

To catch alert from redis and send sightings to MISP, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --redis --alerts
```


To catch alert from eve_json and send sightings to MISP, run the following command:

```bash
iocmite --config /path/to/json/file/settings.json --redis --eve_json
```
