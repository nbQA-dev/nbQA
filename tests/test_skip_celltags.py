"""Test the skip_celltags option."""
import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_skip_celltags_cli(capsys: "CaptureFixture") -> None:
    """
    Check flake8 works. Shouldn't alter the notebook content.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check passing both absolute and relative paths

    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    main(["flake8", path, "--nbqa-skip-celltags=skip-flake8,flake8-skip"])

    out, err = capsys.readouterr()
    expected_out = f"{path}:cell_4:1:1: F401 'random.randint' imported but unused\n"
    expected_err = ""

    assert out == expected_out
    assert err == expected_err


def test_skip_celltags_pyprojecttoml(capsys: "CaptureFixture") -> None:
    """
    Check flake8 works. Shouldn't alter the notebook content.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check passing both absolute and relative paths
    with open("pyproject.toml", "w") as handle:
        handle.write(
            "[tool.nbqa.skip_celltags]\n" 'flake8 = ["skip-flake8", "flake8-skip"]\n'
        )
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    main(["flake8", path])

    out, err = capsys.readouterr()
    expected_out = f"{path}:cell_4:1:1: F401 'random.randint' imported but unused\n"
    expected_err = ""

    assert out == expected_out
    assert err == expected_err
