"""Silly little module which produces unparsable output."""

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()
    for file in args.files:
        print(f"{file}:6174:0 some silly warning")
