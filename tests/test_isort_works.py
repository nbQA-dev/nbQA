import difflib
from pathlib import Path

import pytest

from nbqa.__main__ import main


def test_isort_works(tmp_notebook_for_testing, capsys):
    """
    Check isort works.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["isort", str(Path("tests/data/notebook_for_testing.ipynb"))])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = '+    "import glob\\n",\n' '-    "\\n",\n' '-    "import glob\\n",\n'
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = "Fixing tests/data/notebook_for_testing.ipynb\n"
    expected_err = ""
    assert out == expected_out
    assert err == expected_err


def test_isort_initial_md(tmp_notebook_starting_with_md, capsys):
    """
    Check isort works when a notebook starts with a markdown cell.
    """
    # check diff
    with open(tmp_notebook_starting_with_md, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["isort", "tests/data/notebook_starting_with_md.ipynb"])

    with open(tmp_notebook_starting_with_md, "r") as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = '+    "import glob\\n",\n' '-    "\\n",\n' '-    "import glob\\n",\n'
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = "Fixing tests/data/notebook_starting_with_md.ipynb\n"
    expected_err = ""
    assert out == expected_out
    assert err == expected_err
