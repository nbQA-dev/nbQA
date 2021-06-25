"""Tets running local script."""
import os

from nbqa.__main__ import main


def test_local_script() -> None:
    """Test local script is picked up."""
    cwd = os.getcwd()
    os.chdir(os.path.join("tests", "invalid_data"))
    try:
        main(["foobarqux", "."])
    finally:
        os.chdir(cwd)
