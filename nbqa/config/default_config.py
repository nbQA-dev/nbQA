"""Default configurations."""
from typing import Iterable, Mapping

from nbqa.save_source import CODE_SEPARATOR

DEFAULT_CONFIG: Mapping[str, Mapping[str, Iterable[str]]] = {
    "addopts": {"isort": ("--treat-comment-as-code", CODE_SEPARATOR.rstrip("\n"))},
    "config": {},
    "mutate": {},
    "process_cells": {},
    "diff": {},
    "files": {},
    "exclude": {},
    "skip_bad_cells": {},
}
