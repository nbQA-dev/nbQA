"""Utility functions to deal with paths."""
from pathlib import Path
from typing import Tuple


def remove_prefix(string: str, prefix: str) -> str:
    """
    Remove prefix from string.

    Parameters
    ----------
    string
        Given string to remove prefix from.
    prefix
        Prefix to remove.

    Raises
    ------
    AssertionError
        If string doesn't start with given prefix.
    """
    if string.startswith(prefix):
        string = string[len(prefix) :]
    else:  # pragma: nocover
        raise AssertionError(f"{string} doesn't start with prefix {prefix}")
    return string


def remove_suffix(string: str, suffix: str) -> str:
    """
    Remove suffix from string.

    Parameters
    ----------
    string
        Given string to remove suffix from.
    suffix
        Suffix to remove.

    Raises
    ------
    AssertionError
        If string doesn't end with given suffix.
    """
    if string.endswith(suffix):
        string = string[: -len(suffix)]
    else:  # pragma: nocover
        raise AssertionError(f"{string} doesn't end with suffix {suffix}")
    return string


def get_relative_and_absolute_paths(path: str) -> Tuple[str, str]:
    """Get relative (if possible) and absolute versions of path."""
    absolute_path = Path(path).resolve()
    try:
        relative_path = absolute_path.relative_to(Path.cwd())
    except ValueError:
        relative_path = absolute_path
    return str(relative_path), str(absolute_path)
