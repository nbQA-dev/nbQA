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
        main(["flake8", "."])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = (
        "tests/data/notebook_for_testing.ipynb:cell_1:1:1: F401 'os' imported but unused\n"
        "tests/data/notebook_for_testing.ipynb:cell_1:3:1: F401 'glob' imported but unused\n"
        "tests/data/notebook_for_testing.ipynb:cell_1:5:1: F401 'nbqa' imported but unused\n"
        "tests/data/notebook_for_testing_copy.ipynb:cell_1:1:1: F401 'os' imported but unused\n"
        "tests/data/notebook_for_testing_copy.ipynb:cell_1:3:1: F401 'glob' imported but unused\n"
        "tests/data/notebook_for_testing_copy.ipynb:cell_1:5:1: F401 'nbqa' imported but unused\n"
        "tests/data/notebook_starting_with_md.ipynb:cell_1:1:1: F401 'os' imported but unused\n"
        "tests/data/notebook_starting_with_md.ipynb:cell_1:3:1: F401 'glob' imported but unused\n"
        "tests/data/notebook_starting_with_md.ipynb:cell_1:5:1: F401 'nbqa' imported but unused\n"
        "tests/data/notebook_starting_with_md.ipynb:cell_3:0:1: E303 too many blank lines (3)\n"
        "tests/data/notebook_starting_with_md.ipynb:cell_3:2:1: E302 expected 2 blank lines, found 3\n"
    )
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())
