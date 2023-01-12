#!/usr/bin/env python3

# foi_performance, tool for detecting academic FOI conformance from WDTK API,
# by Martin Keegan

# To the extent (if any) permissible by law, Copyright (C) 2023  Martin Keegan

# This programme is free software; you may redistribute and/or modify it under
# the terms of the Apache Software Licence v2.0.

import logging
import argparse
import json
import csv
import time
import requests
import sys
import io

URL = "https://www.whatdotheyknow.com/body/all-authorities.csv"
DELAY = 2.0 # seconds to delay between requests

def organisations():
    """Get the list of all FOIA-subject organisations."""
    resp = requests.get(URL)
    return io.StringIO(resp.text)

def all_universities():
    """Obtain the name and ID of anything matching a university."""
    for row in csv.reader(organisations()):
        name, code = row[0], row[2]
        if "university" in code:
            yield name, code

def stats(args):
    """Request summaries of FOI performance for each university."""
    for name, code in all_universities():
        url = f"https://www.whatdotheyknow.com/body/{code}.json"
        time.sleep(args.delay)
        resp = requests.get(url).json()
        summary = resp["info"]
        yield name, code, summary

FIELDS = [
    'requests_count',
    'requests_successful_count',
    'requests_not_held_count',
    'requests_overdue_count',
    'requests_visible_classified_count'
]

# items 2-6 of this list must correspond to the FIELDS list above
HEADERS = "Name Total Successful NotHeld Overdue Count Code"

def flatten(args):
    """Make all the info about a university into a single row/tuple."""
    for name, code, summary in stats(args):
        flattened = [summary[k] for k in FIELDS]
        yield tuple([name] + flattened + [code])

def make_csv(args):
    headers = tuple(HEADERS.split())

    w = csv.writer(sys.stdout)
    w.writerow(headers)

    for inst_stat in flatten(args):
        w.writerow(inst_stat)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', required=False,
                    help='set logging level to INFO')
    parser.add_argument('--delay', type=int, default=DELAY,
                        help='override default per-request delay')

    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(20)

    make_csv(args)

if __name__ == '__main__':
    run()
