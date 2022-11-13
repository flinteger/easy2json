#!/usr/bin/env python

import sys
from typing import List


def merge(dest: List[str], list: List[str]) -> int:
    """Merge `list` to `dest`, remove duplicated lines in dest.

    - Returns: skipped lines.
    """
    skipped = 0
    for line in list:
        line = line.strip()
        if len(line) == 0:
            continue

        if line.startswith("!"):
            # ignore comment line
            continue

        if line in dest:
            # print(f"Skip line: {line}")
            skipped += 1
            continue

        dest.append(line)

    return skipped


def main():
    """Merge rule list files to `merged.txt`
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} list1 list2...")
        sys.exit(1)

    dest = []
    skipped = 0
    for file in sys.argv[1:]:
        print(f"Merging {file}")
        with open(file) as f:
            list = f.readlines()
            skipped += merge(dest, list)

    with open(f"merged.txt", "w") as f:
        f.write("\n".join(dest))

    print("Output: merged.txt")
    print(f"Merged lines: {len(dest)}")
    print(f"Skipped lines: {skipped}")


if __name__ == '__main__':
    main()
