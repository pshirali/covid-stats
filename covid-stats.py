#!/usr/bin/env python3

# -----------------------------------------------------------------------------
#
#  COVID-19 Stats Extractor
#
# =============================================================================
#
#  Copyright 2020 Praveen G Shirali
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# -----------------------------------------------------------------------------


import json
import collections
import argparse
import sys
import os
import csv
import logging

from datetime import date, timedelta


__version__ = "0.0.2"


INDIAN_STATE_CODES = [
    'IN',
    'AN', 'AP', 'AR', 'AS', 'BR', 'CH', 'CT', 'DL', 'DN', 'GA', 'GJ', 'HP',
    'HR', 'JH', 'JK', 'KA', 'KL', 'LA', 'MH', 'ML', 'MN', 'MP', 'MZ', 'NL',
    'OR', 'PB', 'PY', 'RJ', 'SK', 'TG', 'TN', 'TR', 'TT', 'UP', 'UT', 'WB'
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d | %(message)s",
    stream=sys.stdout,
    datefmt="%Y-%m-%d %H:%M:%S"
)


class FatalError(Exception):
    pass


def log(msg):
    logging.info(msg)


def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# ---- LICENSE-EXCLUSION -------------------------------------------------------
#
# Sourced from:
# https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
#
def flatten(d, parent_key='', sep='-'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
#
# -----------------------------------------------------------------------------


def verify_continuous_dates(data_all):
    start_date = date(2020, 1, 30)
    today_date = date.today()
    no_of_days = (today_date - start_date).days
    stat_dates = data_all.keys()

    for n in range(no_of_days):
        each_date = start_date + timedelta(days=n)
        if str(each_date) not in stat_dates:
            print("Missing: {}".format(each_date))


def validate_date(datestr, hint):
    ymd = datestr.split("-")
    if not len(ymd) == 3:
        raise ValueError("ERROR: Expected {} date in "
                         "YYYY-MM-DD format".format(hint))
    ymd = [int(e) for e in ymd]
    try:
        return date(year=ymd[0], month=ymd[1], day=ymd[2])
    except Exception:
        err("ERROR: Failed to parse {} date. Invalid input.".format(hint))
        raise


def date_on_or_after(curdate, datestr, hint):
    cur_dt = validate_date(curdate, hint)
    thrshd = validate_date(datestr, hint)
    return True if cur_dt >= thrshd else False


def date_after(curdate, datestr, hint):
    cur_dt = validate_date(curdate, hint)
    thrshd = validate_date(datestr, hint)
    return True if cur_dt > thrshd else False


def fetch_data(args):
    if args.net:
        try:
            import requests
        except ImportError:
            err("ERROR: 'requests' package couldn't be imported")
            err("       Use 'pip install requests' to install this dependency")
            err("       if you wish to pull data directly from the net.")
            raise FatalError("'requests' package not found")
        log("Fetching from URL: {}".format(args.url))
        resp = requests.get(args.url)
        if resp.status_code != 200:
            err("Failed to fetch data from URL: {}".format(args.url))
            err("HTTP Error Code: {}".format(resp.status_code))
            raise FatalError('HTTP Error {} fetching from URL: {}'.format(
                resp.status_code, args.url
            ))
        data = resp.json()
    else:
        if not os.path.exists(args.input_file):
            err("ERROR: The file '{}' does not exist!".format(args.input_file))
            err("You must either have this file available on your local disk")
            err("Or use the option '-n -u' to fetch the data online.")
            raise FatalError("'{}' not found".format(args.input_file))

        log("Attempting to fetch data from file: {}".format(args.input_file))
        with open(args.input_file) as f:
            data = json.load(f)
    log("Data loaded.")
    return data


if __name__ == "__main__":

    ap = argparse.ArgumentParser()

    ap.add_argument(
        "-i", "--input-file", default="data-all.json",
        help="Input json to fetch data from"
    )
    ap.add_argument(
        "-u", "--url", default="https://api.covid19india.org/v4/data-all.json",
        help="URL from which to source data"
    )
    ap.add_argument(
        "-n", "--net", action="store_true",
        help="Fetch data from a URL"
    )
    ap.add_argument(
        "-o", "--output",
        help="Set output file for CSV (optional) or mapping JSON (mandatory)."
    )
    ap.add_argument(
        "-x", "--overwrite", action="store_true",
        help="Overwrite output file if it exists."
    )
    ap.add_argument(
        "-s", "--state", required=True,
        help="Two character Indian state code for which stats must be "
             "processed (Ex: KA, HP etc). Use 'IN' for all-India."
    )
    ap.add_argument(
        "-c", "--columns", action="store_true",
        help="Print only column names as a dict"
    )
    ap.add_argument(
        "-m", "--mapping", help="Path to key-mapping file"
    )
    ap.add_argument(
        "--na", help="Replacement string for 'no-value'", default="0"
    )
    ap.add_argument(
        "--start", help="Include data on or after this date (YYYY-MM-DD)"
    )
    ap.add_argument(
        "--end", help="Exclude data beyond this date (YYYY-MM-DD)"
    )

    if len(sys.argv) == 1:
        ap.print_help(sys.stderr)
        exit(1)

    args = ap.parse_args()

    if args.state not in INDIAN_STATE_CODES:
        err("ERROR: Unknown Indian state. Got: '{}'".format(args.state))
        err("Expected one among: {}".format(INDIAN_STATE_CODES))
        exit(1)

    try:
        if args.start:
            validate_date(args.start, "start")
        if args.end:
            validate_date(args.end, "end")
    except Exception as e:
        err("ERROR: {}".format(e))
        exit(1)

    if not args.output:
        if args.columns:
            err("ERROR: The output file is mandatory when the '-c' switch")
            err("       is in use. Please provide a filename to write the")
            err("       mapping JSON content.")
            exit(1)
        args.output = "covid19-{}.csv".format(args.state)

    if os.path.exists(args.output) and not args.overwrite:
        err("ERROR: The output file '{}' already exists".format(args.output))
        err("       Cannot proceed. Pick a different output file with '-o'")
        err("       or overwrite using '-x'")
        exit(1)

    data = fetch_data(args)
    state_data = {}
    column_names = {"DATE": None}

    for dt in data:
        if args.start and not date_on_or_after(dt, args.start, "start"):
            continue
        if args.end and date_after(dt, args.end, "end"):
            break
        states = INDIAN_STATE_CODES if args.state == "IN" else [args.state]
        for state in states:
            s_data_on_date = data[dt].get(state, {})
            flattened_data = flatten(s_data_on_date, parent_key=state)
            state_data[dt] = {"DATE": dt}
            state_data[dt].update(flattened_data)
            state_colnames = {k: None for k in flattened_data}
            column_names.update(state_colnames)

    if args.columns:
        log("Writing Mapping JSON: {}".format(args.output))
        with open(args.output, 'w') as f:
            f.write(json.dumps({k: k for k in column_names},
                               indent=4, sort_keys=True))
        log("Done.")
        exit(0)

    mapping = {}
    if args.mapping:
        log("Loading mapping from '{}'".format(args.mapping))
        with open(args.mapping) as m:
            mapping = json.load(m)
        if not len(set(column_names.keys()).intersection(set(mapping.keys()))):
            err("ERROR: Didn't find any common keys between the mapping file")
            err("       '{}' and column names.".format(args.mapping))
            exit(1)

    log("Writing CSV data: {}".format(args.output))
    with open(args.output, 'w', newline='') as f:
        csv_w = csv.writer(f, delimiter=',', quotechar='"',
                           quoting=csv.QUOTE_ALL)

        col_to_use = column_names
        if not mapping:
            csv_w.writerow(column_names.keys())
        else:
            csv_w.writerow(mapping.values())
            col_to_use = mapping.keys()

        for r in state_data:
            row_val = [state_data[r].get(k, args.na) for k in col_to_use]
            csv_w.writerow(row_val)
    log("Done.")
