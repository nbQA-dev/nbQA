"""Check configs are picked up when running in different directory."""
import os
from pathlib import Path
from textwrap import dedent

import pytest

from nbqa.__main__ import main


@pytest.mark.parametrize(
    "arg, cwd",
    [
        (Path("tests"), Path.cwd()),
        (Path("data"), Path.cwd() / "tests"),
        (Path("notebook_for_testing.ipynb"), Path.cwd() / "tests/data"),
        (Path.cwd() / "tests/data/notebook_for_testing.ipynb", Path.cwd().parent),
    ],
)
def test_running_in_different_dir_works(arg: Path, cwd: Path, capsys) -> None:
    """
    Check .nbqa.ini config is picked up when running from non-root directory.

    Parameters
    ----------
    arg
        Directory or notebook to run command on.
    cwd
        Directory from which to run command.
    """
    config_path = Path(".nbqa.ini")
    config_path.write_text(
        dedent(
            """\
            [flake8]
            addopts = --ignore=F401 \
            """
        )
    )
    original_cwd = os.getcwd()
    try:
        os.chdir(str(cwd))
        main(["flake8", str(arg)])
        out, _ = capsys.readouterr()
        assert "W291" in out
        assert "F401" not in out
    finally:
        os.chdir(original_cwd)
        Path(".nbqa.ini").unlink()
