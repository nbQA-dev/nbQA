"""Local module with subcommand."""
import argparse
import sys
from typing import Optional, Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Print word (subcommand), ignore paths"""
    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs=1)
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    print(args.word)
    return 0


if __name__ == "__main__":
    sys.exit(main())
