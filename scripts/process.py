#!/usr/bin/env python3

import os
import json
import requests
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

def process_list(list: dict):
    # print(list)
    url = list["url"]
    out = list["out"]
    # print(url, out)
    print(f"Downloading {url}")
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"Got error. status_code={response.status_code} url={url}")
        return

    body = response.text
    basename = os.path.basename(url)
    with open(f"data/{basename}", "w") as f:
        f.write(body)

    print(f"Converting data/{basename}")
    subprocess.run(f"node abp2blocklist.js < data/{basename} > out/{out}", shell=True)

    if os.path.exists(f"out/{out}"):
        with ZipFile(f"out/{out}.zip", "w", ZIP_DEFLATED) as zip:
            zip.write(f"out/{out}", out)

def process(lists: dict):
    for list in lists:
        process_list(list)


def main():
    dirs = ["data", "out"]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)

    with open('lists.json') as f:
        lists = json.load(f)
        process(lists)


if __name__ == '__main__':
    main()
