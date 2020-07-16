import difflib
import platform
from pathlib import Path
from textwrap import dedent

import pytest

from nbqa.__main__ import main


def test_pytest_doctest_works(tmp_notebook_for_testing, capsys):
    """
    Check pytest --doctest-modules works.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["pytest", "--doctest-modules"])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = dedent(
        f"""\
        ============================= test session starts ==============================
        platform {platform.system().lower()} -- Python {platform.python_version()}, pytest-5.4.3, py-1.9.0, pluggy-0.13.1
        rootdir: {str(Path.cwd())}
        plugins: cov-2.10.0
        collected 2 items

        tests/data/notebook_for_testing.ipynb .                                     [ 50%]
        tests/data/notebook_for_testing_copy.ipynb .                                [100%]

        ============================== 2 passed in 0.03s ===============================
        """  # noqa
    )
    expected_err = ""
    assert out == expected_out
    assert err == expected_err
