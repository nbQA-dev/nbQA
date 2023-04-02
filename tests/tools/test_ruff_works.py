"""Check :code:`ruff` works as intended."""

import os
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


@pytest.mark.parametrize(
    "path_0, path_1, path_2",
    (
        (
            os.path.abspath(
                os.path.join("tests", "data", "notebook_for_testing.ipynb")
            ),
            os.path.abspath(
                os.path.join("tests", "data", "notebook_for_testing_copy.ipynb")
            ),
            os.path.abspath(
                os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
            ),
        ),
        (
            os.path.join("tests", "data", "notebook_for_testing.ipynb"),
            os.path.join("tests", "data", "notebook_for_testing_copy.ipynb"),
            os.path.join("tests", "data", "notebook_starting_with_md.ipynb"),
        ),
    ),
)
def test_ruff_works(
    path_0: str, path_1: str, path_2: str, capsys: "CaptureFixture"
) -> None:
    """
    Check flake8 works. Shouldn't alter the notebook content.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check passing both absolute and relative paths

    main(["ruff", path_0, path_1, path_2])

    expected_path_0 = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    expected_path_1 = os.path.join("tests", "data", "notebook_for_testing_copy.ipynb")
    expected_path_2 = os.path.join("tests", "data", "notebook_starting_with_md.ipynb")

    out, err = capsys.readouterr()
    expected_out = (
        f"{expected_path_1}:cell_1:1:8: F401 [*] `os` imported but unused\n"
        f"{expected_path_1}:cell_1:3:8: F401 [*] `glob` imported but unused\n"
        f"{expected_path_1}:cell_1:5:8: F401 [*] `nbqa` imported but unused\n"
        f"{expected_path_0}:cell_1:1:8: F401 [*] `os` imported but unused\n"
        f"{expected_path_0}:cell_1:3:8: F401 [*] `glob` imported but unused\n"
        f"{expected_path_0}:cell_1:5:8: F401 [*] `nbqa` imported but unused\n"
        f"{expected_path_0}:cell_4:1:1: E402 Module level import not at top of file\n"
        f"{expected_path_0}:cell_4:1:20: F401 [*] `random.randint` imported but unused\n"
        f"{expected_path_0}:cell_5:1:1: E402 Module level import not at top of file\n"
        f"{expected_path_0}:cell_5:2:1: E402 Module level import not at top of file\n"
        f"{expected_path_2}:cell_1:1:8: F401 [*] `os` imported but unused\n"
        f"{expected_path_2}:cell_1:3:8: F401 [*] `glob` imported but unused\n"
        f"{expected_path_2}:cell_1:5:8: F401 [*] `nbqa` imported but unused\n"
        "Found 13 errors.\n"
        "[*] 10 potentially fixable with the --fix option.\n"
    )
    assert "\n".join(sorted(out.replace("\r\n", "\n").splitlines())) == "\n".join(
        sorted(expected_out.splitlines())
    )
    assert err == ""


def test_cell_with_all_magics(capsys: "CaptureFixture") -> None:
    """
    Should ignore cell with all magics.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """

    path = os.path.join("tests", "data", "all_magic_cell.ipynb")
    main(["ruff", path])

    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_ruff_isort(capsys: "CaptureFixture") -> None:
    """
    Should ignore cell with all magics.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """

    path = os.path.join("tests", "data", "simple_imports.ipynb")
    main(["ruff", path, "--select=I"])

    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
