"""
Check that :code:`black` works as intended.
"""

import difflib
import os
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.capture import CaptureFixture


def test_black_works(
    tmp_notebook_for_testing: "Path", capsys: "CaptureFixture"
) -> None:
    """
    Check black works. Should only reformat code cells.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    with pytest.raises(SystemExit):
        main(["black", path])
    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = (
        "-    \"    return f'hello {name}'\\n\",\n"
        '+    "    return f\\"hello {name}\\"\\n",\n'
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = os.linesep.join(
        [f"reformatted {path}", "All done!   ", "1 file reformatted."]
    )
    assert out == expected_out
    for i in (0, 2):  # haven't figured out how to test the emojis part
        assert err.splitlines()[i] == expected_err.splitlines()[i]
