import difflib
from pathlib import Path

import pytest

from nbqa.__main__ import main


def test_nbqa_ini_works(tmp_notebook_for_testing, capsys):
    """
    Check .nbqa.ini config is picked up works.
    """

    with open(".nbqa.ini", "w") as f:
        f.write("[flake8]\nignore=F401\nselect=E303\n")

    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["flake8", ".", "--ignore", "E302"])

    Path(".nbqa.ini").unlink()

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = "tests/data/notebook_starting_with_md.ipynb:cell_3:0:1: E303 too many blank lines (3)\n"
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())
