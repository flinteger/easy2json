#!/usr/bin/env python3

import os
import logging
import json
import requests
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED
from merge import merge


def dump_rules_info(filepath: str):
    with open(filepath) as f:
        rules = json.load(f)
        rules_count = len(rules)
        max_unless_domain_count = 0
        max_if_domain_count = 0
        max_selector_count = 0
        for rule in rules:
            trigger = rule["trigger"]
            action = rule["action"]
            if "if-domain" in trigger:
                count = len(trigger["if-domain"])
                if count > max_if_domain_count:
                    max_if_domain_count = count
            if "unless-domain" in trigger:
                count = len(trigger["unless-domain"])
                if count > max_unless_domain_count:
                    max_unless_domain_count = count

            if "selector" in action:
                count = len(action["selector"].split(","))
                if count > max_selector_count:
                    max_selector_count = count

        print(f"file={filepath} rules_count={rules_count} max_if_domain_count={max_if_domain_count} max_unless_domain_count={max_unless_domain_count} max_selector_count={max_selector_count}")


def process_list(list: dict):
    urls = list["urls"]
    out = list["out"]   # json output filename. e.g. easylist.json
    outjson = os.path.join("out", out)  # e.g. out/easylist.json
    outtxt = os.path.join("out", out.split(".")[0] + ".txt")

    extratxt = os.path.join("extra", out.split(".")[0] + ".txt")  # optional extra rules

    if os.path.exists(outtxt):
        # delete old file if exist.
        os.unlink(outtxt)

    merged = []     # merged rules
    skipped = 0     # skipped rules count
    for url in urls:
        logging.info(f"Downloading {url}")
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            logging.error(f"Got error. status_code={response.status_code} url={url}")
            return

        body = response.text
        lines = body.splitlines(keepends=False)
        skipped += merge(merged, lines)
        logging.info(f"Processed rules in {url}. skipped={skipped}")

    if os.path.exists(extratxt):
        # Append extra rules if exist.
        logging.info(f"Merging {extratxt}")
        with open(extratxt) as f:
            list = f.readlines()
            skipped += merge(merged, list)

    with open(outtxt, "w") as f:
        f.write("\n".join(merged))

    logging.info(f"Wrote {outtxt}, lines={len(merged)} skipped={skipped}")

    logging.info(f"Converting {outtxt} to {outjson}")
    # subprocess.run(f"node abp2blocklist.js < {outtxt} > {outjson}", shell=True)
    subprocess.run(f"cat {outtxt} | ./bin/ConverterTool.Darwin -s 15 -o true -O {outjson}", shell=True)

    dump_rules_info(outjson)

    if os.path.exists(outjson):
        # compress to reduce file size.
        with ZipFile(f"{outjson}.zip", "w", ZIP_DEFLATED) as zip:
            zip.write(outjson, out)


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
        if len(input_list) != 0:
            lists = list(filter(lambda list: list["id"] in input_list, lists))
            # print(lists)
        process(lists)


if __name__ == '__main__':
    """
    Usage:
        ./scripts/process.py
        ./scripts/process.py <id>...
        ./scripts/process.py fr sp
    """
    main()
