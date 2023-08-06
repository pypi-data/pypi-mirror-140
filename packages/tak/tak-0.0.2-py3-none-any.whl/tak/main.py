#!/usr/bin/env python

import pkg_resources  # part of setuptools
import json
import time
import sys
import os
import argparse


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Play a game of Tak.  Not written yet.")
    parser.add_argument('--ai', type=bool)
    args = parser.parse_args(argv)

    if args.version:
        pkg = pkg_resources.require('tak')
        print(f'{sys.argv[0]} {pkg[0].version}')
        exit(0)

    print("This game hasn't been written yet.")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
