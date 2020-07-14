import difflib

import pytest

from nbqa.__main__ import main


def test_flake8_works(tmp_notebook_for_testing, capsys):
    """
    Check flake8 works. Shouldn't alter the notebook content.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["flake8"])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = (
        "notebook_for_testing.ipynb:cell_1:1:1: F401 'pandas as pd' imported but unused\n"
        "notebook_for_testing.ipynb:cell_1:3:1: F401 'numpy as np' imported but unused\n"
        "notebook_for_testing.ipynb:cell_1:5:1: F401 'os' imported but unused\n"
    )
    expected_err = ""
    assert out == expected_out
    assert err == expected_err
