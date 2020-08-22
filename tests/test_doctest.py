"""Check that running :code:`doctest` works."""

import os
from pathlib import Path
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


def test_doctest_works(
    tmp_notebook_for_testing: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check doctest works.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
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

    expected_out = dedent(
        f"""\
        **********************************************************************
        File "{os.path.abspath(WRONG_EXAMPLE_NOTEBOOK)}", cell_2:11, in notebook_for_testing_copy   .hello
        Failed example:
            hello("goodbye")
        Expected:
            'hello goodby'
        Got:
            'hello goodbye'
        **********************************************************************
        1 items had failures:
           1 of   2 in notebook_for_testing_copy   .hello
        ***Test Failed*** 1 failures.
        """
    )

    assert out == expected_out
    assert err == ""
