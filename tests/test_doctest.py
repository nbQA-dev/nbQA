import difflib
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pytest_doctest_works(
    tmp_notebook_for_testing: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check pytest --doctest-modules works.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["pytest", "--doctest-modules", "."])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_err = ""
    assert f"rootdir: {str(Path.cwd())}" in out.splitlines()[2]
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

    print(out.splitlines())

    assert err == expected_err
