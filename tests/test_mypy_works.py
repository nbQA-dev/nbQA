import difflib
from textwrap import dedent

import pytest

from nbqa.__main__ import main


def test_mypy_works(tmp_notebook_for_testing, capsys):
    """
    Check flake8 works. Shouldn't alter the notebook content.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["mypy", "--ignore-missing-imports"])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = dedent(
        """\
        tests/data/notebook_for_testing_copy.ipynb:cell_2:18: error: Argument 1 to "hello" has incompatible type "int"; expected "str"
        tests/data/notebook_for_testing.ipynb:cell_2:18: error: Argument 1 to "hello" has incompatible type "int"; expected "str"
        Found 2 errors in 2 files (checked 5 source files)
        """  # noqa
    )
    expected_err = ""
    assert out == expected_out
    assert err == expected_err
