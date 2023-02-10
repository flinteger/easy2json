#!/usr/bin/env python3

import datetime
import json
import hashlib
import logging
import os
import subprocess
from typing import List
from zipfile import ZIP_DEFLATED, ZipFile

import requests
from merge import merge
from preprocess import preprocess


def parse_metadata(lines: List[str]) -> dict:
    """
    Example metadata

    [Adblock Plus 2.0]
    ! Checksum: 8Utys+Cpw0P+1E1zjU2ocg
    ! Version: 202211170341
    ! Title: KoreanList
    ! Last modified: 17 Nov 2022 03:41 UTC
    ! Expires: 1 days (update frequency)
    ! Homepage: https://forums.lanik.us/viewforum.php?f=111
    ! Licence: https://easylist.to/pages/licence.html
    !

    Not all the list have metadata.
    """
    metadata = {}
    max = 100
    i = 0
    for line in lines:
        if line.startswith("! Last modified: "):
            (_, value) = line.split(": ", 1)
            last_modified = datetime.datetime.strptime(value, "%d %b %Y %H:%M %Z")
            metadata["updated_ts"] = last_modified.timestamp()
            break

        i += 1
        if i == max:
            break

    return metadata


def format_json_file(filepath: str):
    """Re-format json to ndjson."""
    lines = []
    rules = []

    with open(filepath) as f:
        rules = json.load(f)

    for rule in rules:
        # No need escape /
        rule["trigger"]["url-filter"] = rule["trigger"]["url-filter"].replace("\\/", "/")
        line = json.dumps(rule, separators=(',', ':'), sort_keys=True)  # dump into a single line without any space.
        lines.append(line)

    with open(filepath, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")


def dump_rules_info(filepath: str) -> int:
    """Returns total rules count."""
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
        return rules_count


def process_list(list: dict):
    id = list["id"]
    urls = list["urls"]
    out = list["out"]   # json output filename. e.g. easylist.json
    outjson = os.path.join("out", out)  # e.g. out/easylist.json
    outtxt = os.path.join("out", out.split(".")[0] + ".txt")

    extratxt = os.path.join("extra", out.split(".")[0] + ".txt")  # optional extra rules

    if os.path.exists(outtxt):
        # delete old file if exist.
        os.unlink(outtxt)

    merged = []     # merged rules
    total_skipped = 0     # skipped rules count
    for url in urls:
        logging.info(f"Downloading {url}")
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            logging.error(f"Got error. status_code={response.status_code} id={id} url={url}")
            return

        body = response.text
        lines = body.splitlines(keepends=False)  # lines without '\n'

        # metadata = parse_metadata(lines)

        skipped = merge(merged, lines)
        total_skipped += skipped
        logging.info(f"Processed rules in {url}. id={id} skipped={skipped} total_skipped={total_skipped}")

    if os.path.exists(extratxt):
        # Append extra rules if exist.
        logging.info(f"Merging {extratxt}")
        with open(extratxt) as f:
            skipped = merge(merged, f.readlines())
            total_skipped += skipped

    merged.append(f"||example.com/b/{id}|")

    with open(outtxt, "w") as f:
        f.write("\n".join(merged))

    final_rules_count = preprocess(outtxt)

    original_rules_count = len(merged)
    skipped_non_top1m = original_rules_count - final_rules_count

    logging.info(f"Wrote to {outtxt} successfully. id={id} original_rules_count={original_rules_count} final_rules_count={final_rules_count} total_skipped={total_skipped} skipped_non_top1m={skipped_non_top1m}")

    logging.info(f"Converting {outtxt} to {outjson}. id={id}")
    # subprocess.run(f"node abp2blocklist.js < {outtxt} > {outjson}", shell=True)
    subprocess.run(f"cat {outtxt} | ./bin/ConverterTool.Darwin -s 15 -o true -O {outjson}", shell=True)

    rules_count = dump_rules_info(outjson)

    format_json_file(outjson)

    if os.path.exists(outjson):
        # compress to reduce file size.
        out_zip = f"{outjson}.zip"
        with ZipFile(out_zip, "w", ZIP_DEFLATED) as zip:
            zip.write(outjson, out)

        with open(out_zip, "rb") as f:
            # digest = hashlib.file_digest(f, "sha256")  # requires Python 3.11
            digest = hashlib.sha256(f.read())
            list["digest"] = digest.hexdigest()

    now = datetime.datetime.now()
    list["created_ts"] = int(now.timestamp())
    list["original_rules_count"] = original_rules_count
    list["json_rules_count"] = rules_count


def process(lists: dict):
    for list in lists:
        process_list(list)

    with open(f"out/lists.json", "w") as f:
        json.dump(lists, f, ensure_ascii=False, sort_keys=True)


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
