"""Import importlib.metadata, using backport if on an old version of Python."""

from importlib import import_module

metadata = import_module("importlib.metadata")
