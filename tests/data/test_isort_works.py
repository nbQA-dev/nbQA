import difflib

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
        main(["--command=isort", "tests/data/notebook_for_testing.ipynb"])

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
