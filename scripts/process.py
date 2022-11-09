#!/usr/bin/env python3

import os
import logging
import json
import requests
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

def process_list(list: dict):
    url = list["url"]   # source URL
    out = list["out"]   # json output filename. e.g. easylist.json
    extra = out.split(".")[0] + ".txt"  # optional extra rules

    logging.info(f"Downloading {url}")
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        logging.error(f"Got error. status_code={response.status_code} url={url}")
        return

    body = response.text
    basename = os.path.basename(url)
    with open(f"data/{basename}", "w") as f:
        f.write(body)

        if os.path.exists(f"extra/{extra}"):
            # Append extra rules if exist.
            logging.info(f"Appending extra/{extra} to data/{basename}")
            with open(f"extra/{extra}") as ex:
                f.write("\n")
                f.write(ex.read())

    logging.info(f"Converting data/{basename} to out/{out}")
    subprocess.run(f"node abp2blocklist.js < data/{basename} > out/{out}", shell=True)

    if os.path.exists(f"out/{out}"):
        # compress to reduce file size.
        with ZipFile(f"out/{out}.zip", "w", ZIP_DEFLATED) as zip:
            zip.write(f"out/{out}", out)


def process(lists: dict):
    for list in lists:
        process_list(list)


def setup_logging():
    datefmt = "%Y-%m-%dT%H:%M:%S%Z"
    # format = "%(asctime)s pid=%(process)d tid=%(thread)d logger=%(name)s level=%(levelname)s %(message)s"
    # format = "%(asctime)s %(thread)d %(levelname)s %(message)s"
    format = "%(asctime)s %(levelname)s %(message)s"
    logging.basicConfig(
        # filename='process.log',
        level=logging.INFO,
        datefmt=datefmt,
        format=format)

def main():
    setup_logging()
    dirs = ["data", "out"]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)

    with open('lists.json') as f:
        lists = json.load(f)
        import sys
        input_list = sys.argv[1:]
        print(input_list)
        if len(input_list) != 0:
            lists = list(filter(lambda list: list["id"] in input_list, lists))
            print(lists)
        process(lists)


if __name__ == '__main__':
    """
    Usage:
        ./scripts/process.py
        ./scripts/process.py <id>...
        ./scripts/process.py fr sp
    """
    main()
