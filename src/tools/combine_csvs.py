#!/usr/bin/env python

import gzip
import codecs
import random
import csv
from steamroller.tools.io import reader, writer

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument(nargs="+", dest="inputs")
    options = parser.parse_args()

    key_fields = ["task", "fold", "model", "size"]
    fields = set()
    rows = {}
    for ifile in options.inputs:
        with open(ifile) as ifd:
            for entry in csv.DictReader(ifd, delimiter="\t"):
                key = tuple([entry[f] for f in key_fields])
                rows[key] = rows.get(key, {})
                for k, v in entry.items():
                    fields.add(k)
                    if k not in key_fields:
                        rows[key][k] = v
                    

    with open(options.output, "w") as ofd:
        c = csv.DictWriter(ofd, fieldnames=fields, delimiter="\t")
        c.writeheader()
        for fs, r in rows.items():
            c.writerow({k : v for k, v in list(zip(key_fields, fs)) + list(r.items())})

