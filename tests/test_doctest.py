"""Check that running :code:`pytest` with the :code:`--doctest-modules` flag works."""

import difflib
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pytest_doctest_works(
    tmp_notebook_for_testing: Path, capsys: "CaptureFixture",
) -> None:
    """
    Check pytest --doctest-modules works.

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
    with pytest.raises(SystemExit):
        main(["pytest", "--doctest-modules", "tests"])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    (out, err) = capsys.readouterr()
    expected_err = ""
    print(out)
    print(err)
    assert any(f"rootdir: {str(Path.cwd())}" in i for i in out.splitlines())
    assert any(
        os.path.join("tests", "data", "notebook_for_testing.ipynb") in i
        for i in out.splitlines()
    )
    assert any(
        os.path.join("tests", "data", "notebook_for_testing_copy.ipynb") in i
        for i in out.splitlines()
    )
    assert any(
        os.path.join("tests", "data", "notebook_starting_with_md.ipynb") in i
        for i in out.splitlines()
    )
    assert re.match(r"\.py\s", out) is None

    assert err == expected_err
