"""Check that running :code:`doctest` works."""

import os
import sys
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
GOOD_EXAMPLE_NOTEBOOK = os.path.join("tests", "data", "notebook_for_testing.ipynb")
WRONG_EXAMPLE_NOTEBOOK = os.path.join(
    "tests", "data", "notebook_for_testing_copy.ipynb"
)
INVALID_IMPORT_NOTEBOOK = os.path.join(
    "tests", "data", "invalid_import_in_doctest.ipynb"
)


def test_doctest_works(capsys: "CaptureFixture") -> None:
    """
    Check doctest works.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    main(["doctest", GOOD_EXAMPLE_NOTEBOOK])

    # check out and err
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""

    main(["doctest", WRONG_EXAMPLE_NOTEBOOK])

    # check out and err
    out, err = capsys.readouterr()

    expected_out = (
        "**********************************************************************\n"
        f'File "{WRONG_EXAMPLE_NOTEBOOK}", cell_2:10, in notebook_for_testing_copy.hello\n'
        "Failed example:\n"
        '    hello("goodbye")\n'
        "Expected:\n"
        "    'hello goodby'\n"
        "Got:\n"
        "    'hello goodbye'\n"
        "**********************************************************************\n"
        "1 items had failures:\n"
        "   1 of   2 in notebook_for_testing_copy.hello\n"
        "***Test Failed*** 1 failures.\n"
    )
    if sys.version_info >= (3, 13):
        expected_out = expected_out.replace("1 failures", "1 failure")
        expected_out = expected_out.replace("1 items", "1 item")

    try:
        assert out.replace("\r\n", "\n") == expected_out
    except AssertionError:
        # observed this in CI, some jobs pass with absolute path,
        # others with relative...
        assert out.replace("\r\n", "\n") == expected_out.replace(
            WRONG_EXAMPLE_NOTEBOOK, os.path.abspath(WRONG_EXAMPLE_NOTEBOOK)
        )
    assert err == ""


def test_doctest_invalid_import(capsys: "CaptureFixture") -> None:
    """
    Check that correct error is reported if notebook contains unimportable imports.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    main(["doctest", INVALID_IMPORT_NOTEBOOK])

    _, err = capsys.readouterr()
    assert "ModuleNotFoundError: No module named 'thisdoesnotexist'" in err
