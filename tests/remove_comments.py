"""
Silly little module which removes comments.

This is just so we can check what happens when running nbqa on a tool which causes a failure.
"""

import argparse
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args, _ = parser.parse_known_args()
    file_ = Path(args.path).read_text()
    file_ = file_.replace("#", "")
    Path(args.path).write_text(file_)
