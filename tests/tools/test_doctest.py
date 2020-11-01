"""Check that running :code:`doctest` works."""

import os
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

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
    with pytest.raises(SystemExit):
        main(["doctest", GOOD_EXAMPLE_NOTEBOOK])

    # check out and err
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""

    with pytest.raises(SystemExit):
        main(["doctest", WRONG_EXAMPLE_NOTEBOOK])

    # check out and err
    out, err = capsys.readouterr()

    # pylint: disable=C0301
    expected_out = dedent(
        f"""\
        **********************************************************************
        File "{WRONG_EXAMPLE_NOTEBOOK}", cell_2:10, in notebook_for_testing_copy.hello
        Failed example:
            hello("goodbye")
        Expected:
            'hello goodby'
        Got:
            'hello goodbye'
        **********************************************************************
        1 items had failures:
           1 of   2 in notebook_for_testing_copy.hello
        ***Test Failed*** 1 failures.
        """
    )

    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert err == ""


def test_doctest_invalid_import(capsys: "CaptureFixture") -> None:
    """
    Check that correct error is reported if notebook contains unimportable imports.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    with pytest.raises(SystemExit):
        main(["doctest", INVALID_IMPORT_NOTEBOOK])

    _, err = capsys.readouterr()
    assert "ModuleNotFoundError: No module named 'thisdoesnotexist'" in err
