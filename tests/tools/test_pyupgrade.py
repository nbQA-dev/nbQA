"""Check pyupgrade works."""

import difflib
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:

    from _pytest.capture import CaptureFixture


def test_pyupgrade(tmp_notebook_for_testing: Path, capsys: "CaptureFixture") -> None:
    """
    Check pyupgrade works. Should only reformat code cells.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`tmp_notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_for_testing) as handle:
        before = handle.readlines()
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))

    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.mutate]
            pyupgrade = 1

            [nbqa.addopts]
            pyupgrade = '--py36-plus'
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["pyupgrade", path])
    Path("setup.cfg").unlink()
    with open(tmp_notebook_for_testing) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = (
        "-    \"    return 'hello {}'.format(name)\\n\",\n"
        "+    \"    return f'hello {name}'\\n\",\n"
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = f"Rewriting {path}{os.linesep}"
    assert out == expected_out
    assert err == expected_err
