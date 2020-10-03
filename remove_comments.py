"""
Silly little module which removes comments.

This is just so we can check what happens when running nbqa on a tool which causes a failure.
"""

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    with open(args.path) as handle:
        file_ = handle.read()
    file_ = file_.replace("#", "")
    with open(args.path, "w") as handle:
        handle.write(file_)
