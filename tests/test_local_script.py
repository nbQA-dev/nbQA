"""Tets running local script."""
import os
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


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


def test_local_submodule() -> None:
    """Test local submodule is picked up."""
    cwd = os.getcwd()
    os.chdir(os.path.join("tests", "invalid_data"))
    try:
        main(["mymod.mysubmod", "."])
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


def test_with_subcommand(capsys: "CaptureFixture") -> None:
    """Check subcommand is picked up by module."""
    main(["tests.local_script foo", "."])
    out, _ = capsys.readouterr()
    assert out.replace("\r\n", "\n") == "['foo']\n"
