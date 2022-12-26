"""Check that running :code:`pydocstyle` works."""

import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pydocstyle_works(capsys: "CaptureFixture") -> None:
    """
    Check pydocstyle works.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    main(["pydocstyle", path])

    # check out and err
    out, err = capsys.readouterr()
    expected_out = (
        f"{path}:cell_1:0 at module level:\n"
        "        D100: Missing docstring in public module\n"
        f"{path}:cell_2:3 in public function `hello`:\n"
        "        D202: No blank lines allowed after function docstring (found 1)\n"
        f"{path}:cell_2:3 in public function `hello`:\n"
        '        D301: Use r""" if any backslashes in a docstring\n'
    )
    assert out.replace("\r\n", "\n") == expected_out
    assert err == ""
