#!/usr/bin/python3
from pycid_dev.lib.authentication.authentication import Authentication
import argparse


def main(args):
    Authentication(generate_new=args.generate, verbose=args.verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="Run this tool to refresh authentication (must be done every hour) or create authentication (using '-g')")
    parser.add_argument('-g', '--generate', action='store_true',
                        help="Generate a new third-party token. ")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Print verbosely.")
    args = parser.parse_args()

    main(args)
