"""Tets running local script."""
import os

import pytest

from nbqa.__main__ import main


def test_local_script() -> None:
    """Test local script is picked up."""
    cwd = os.getcwd()
    os.chdir(os.path.join("tests", "invalid_data"))
    try:
        main(["foobarqux", "."])
    finally:
        os.chdir(cwd)


def test_local_module() -> None:
    """Test local module is picked up."""
    cwd = os.getcwd()
    os.chdir(os.path.join("tests", "invalid_data"))
    try:
        main(["mymod", "."])
    finally:
        os.chdir(cwd)


def test_local_nonfound() -> None:
    """Test local module is picked up."""
    cwd = os.getcwd()
    os.chdir(os.path.join("tests", "invalid_data"))
    try:
        with pytest.raises(ModuleNotFoundError):
            main(["fdsfda", "."])
    finally:
        os.chdir(cwd)
