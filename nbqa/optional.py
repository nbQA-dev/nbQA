"""Import importlib.metadata, using backport if on an old version of Python."""

from importlib import import_module

try:
    # python 3.8 and above
    metadata = import_module("importlib.metadata")
except ImportError:  # pragma: nocover
    # (coverage is calculated using Python3.8, but we test for Python3.7 anyway)
    # python 3.7 and below
    metadata = import_module("importlib_metadata")
