"""
Silly little module which removes cell content except for first lne.

This is just so we can check what happens when running nbqa on a tool which causes a failure.
"""


import argparse
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args, _ = parser.parse_known_args()
    file_ = Path(args.path).read_text()
    newlines = [line + "\n" for line in file_.splitlines() if line.startswith("#")]
    Path(args.path).write_text("\n".join(newlines))
