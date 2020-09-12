"""Check configs from :code:`.nbqa.ini` are picked up."""
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest


@pytest.mark.parametrize(
    "arg, cwd",
    [
        ("tests", Path.cwd()),
        ("data", Path.cwd() / "tests"),
        ("notebook_for_testing.ipynb", Path.cwd() / "tests/data"),
    ],
)
def test_running_in_different_dir_works(arg: Path, cwd: Path) -> None:
    """
    Check .nbqa.ini config is picked up works.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    with open(".nbqa.ini", "w") as handle:
        handle.write(
            dedent(
                """\
            [flake8]
            addopts = --ignore=F401 \
            """
            )
        )

    output = subprocess.run(
        ["nbqa", "flake8", arg], stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd
    )

    Path(".nbqa.ini").unlink()

    out = output.stdout.decode()
    assert "W291" in out
    assert "F401" not in out
