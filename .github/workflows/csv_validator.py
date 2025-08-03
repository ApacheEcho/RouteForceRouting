#!/usr/bin/env python3
"""
csv_validator.py
================

This module validates the format of a CSV file intended for importing issues
into GitHub. It checks for the presence of required headers and reports
rows with missing required data.

Usage:
    python csv_validator.py path/to/csv

Exit status:
    0 – CSV is valid
    1 – CSV is missing required headers or has invalid rows

"""

import csv
import os
import sys


REQUIRED_HEADERS = {"title", "body", "labels"}
OPTIONAL_HEADERS = {"assignee"}


def validate_csv(path: str) -> bool:
    """Validate that the CSV contains required headers and data.

    :param path: Path to the CSV file.
    :return: True if valid, False otherwise.
    """
    if not os.path.isfile(path):
        print(f"CSV file does not exist: {path}")
        return False
    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print("CSV file has no headers")
            return False
        headers = {name.lower() for name in reader.fieldnames}
        missing = REQUIRED_HEADERS - headers
        extra_headers = headers - REQUIRED_HEADERS - OPTIONAL_HEADERS
        if missing:
            print(f"Missing required headers: {', '.join(sorted(missing))}")
            return False
        if extra_headers:
            # Warn about unexpected headers but do not mark invalid
            print(f"Warning: Unexpected headers detected: {', '.join(sorted(extra_headers))}")
        valid = True
        row_num = 1  # account for header row
        for row in reader:
            row_num += 1
            for field in REQUIRED_HEADERS:
                value = row.get(field, "").strip()
                if not value:
                    print(f"Row {row_num}: missing required field '{field}'.")
                    valid = False
        return valid


def main(args: list[str]) -> int:
    if len(args) != 2:
        print("Usage: python csv_validator.py <path_to_csv>")
        return 1
    csv_file = args[1]
    if validate_csv(csv_file):
        print(f"CSV '{csv_file}' is valid.")
        return 0
    else:
        print(f"CSV '{csv_file}' is invalid.")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))