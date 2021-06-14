"""Default configurations."""
from typing import Mapping, Sequence

from nbqa.save_source import CODE_SEPARATOR

DEFAULT_CONFIG: Mapping[str, Mapping[str, Sequence[str]]] = {
    "addopts": {"isort": ("--treat-comment-as-code", CODE_SEPARATOR.rstrip("\n"))},
    "config": {},
    "mutate": {},
    "process_cells": {},
    "diff": {},
    "files": {},
    "exclude": {},
    "skip_bad_cells": {},
}
