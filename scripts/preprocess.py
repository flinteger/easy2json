#!/usr/bin/env python3
import sys
from typing import Optional

def readTop1mDomains():
    with open('data/top1m.domains') as f:
        domains = set()
        for line in f.readlines():
            line = line.strip()
            domains.add(line)
        return domains

top1mDomains = readTop1mDomains()

def _processLine(line: str) -> Optional[str]:
    domain = None
    if line.startswith("||") or line.startswith("@@||"):
        # ||rumblyjouking.store^
        # ||annahar.com/assets/js/notifications.js
        # @@||torrentfreak.com/images/reddit$image

        endIndex = line.find("^")
        if endIndex == -1:
            endIndex = line.find("/")

        if endIndex == -1:
            return line

        startIndex = 2 if line.startswith("||") else 4
        domain = line[startIndex:endIndex]
    elif line.find("##") != -1 or line.find("#@#") != -1:
        # qidian.com##.focus-img
        # 4399.cn,cna.com.tw,cts.com.tw,digitimes.com.tw,weather.com.cn##.gotop
        endIndex = line.find("#@#")
        if endIndex == -1:
            endIndex = line.find("##")
        domain = line[0:endIndex]

    # print(f"line={line} domain={domain}")

    if not domain:
        return line

    if domain.find(",") != -1 or domain.find("*") != -1:
        return line

    if domain in top1mDomains:
        return line
    # print(f"Filter out domain: {domain}")
    return None


def preprocess(blocklistFile: str) -> int:
    lines = []
    with open(blocklistFile) as f:
        for line in f.readlines():
            line = line.strip()
            line = _processLine(line)
            if line:
                lines.append(line)

    with open(blocklistFile, "w") as f:
        f.write('\n'.join(lines))

    return len(lines)


if __name__ == '__main__':
    # preprocess('out/easybase.txt')
    # preprocess('testrules.txt')
    blocklistFile = sys.argv[1]
    preprocess(blocklistFile)
    pass
