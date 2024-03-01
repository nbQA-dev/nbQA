"""Check that :code:`black` works as intended."""

import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pylint_works(capsys: "CaptureFixture") -> None:
    """
    Check pylint works. Check all the warnings raised by pylint on the notebook.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # Pass one file with absolute path and the other one with relative path
    notebook1 = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    notebook2 = os.path.join("tests", "data", "notebook_with_indented_magics.ipynb")

    main(["pylint", notebook1, notebook2, "--disable=C0114"])

    # check out and err
    out, _ = capsys.readouterr()

    expected_out = (
        "************* Module tests.data.notebook_for_testing\n"
        f"{notebook1}:cell_2:19:8: C0303: Trailing whitespace (trailing-whitespace)\n"  # noqa: E501
        f"{notebook1}:cell_2:15:11: C0209: Formatting a regular string which could be an f-string (consider-using-f-string)\n"  # noqa: E501
        f'{notebook1}:cell_4:1:0: C0413: Import "from random import randint" should be placed at the top of the module (wrong-import-position)\n'  # noqa: E501
        f'{notebook1}:cell_5:1:0: C0413: Import "import pprint" should be placed at the top of the module (wrong-import-position)\n'  # noqa: E501
        f'{notebook1}:cell_5:2:0: C0413: Import "import sys" should be placed at the top of the module (wrong-import-position)\n'  # noqa: E501
        f'{notebook1}:cell_4:1:0: C0411: standard import "random.randint" should be placed before first party import "nbqa"  (wrong-import-order)\n'  # noqa: E501
        f'{notebook1}:cell_5:1:0: C0411: standard import "pprint" should be placed before first party import "nbqa"  (wrong-import-order)\n'  # noqa: E501
        f'{notebook1}:cell_5:2:0: C0411: standard import "sys" should be placed before first party import "nbqa"  (wrong-import-order)\n'  # noqa: E501
        f"{notebook1}:cell_1:1:0: W0611: Unused import os (unused-import)\n"
        f"{notebook1}:cell_1:3:0: W0611: Unused import glob (unused-import)\n"
        f"{notebook1}:cell_1:5:0: W0611: Unused import nbqa (unused-import)\n"
        f"{notebook1}:cell_4:1:0: W0611: Unused randint imported from random (unused-import)\n"
        "************* Module tests.data.notebook_with_indented_magics\n"
        f'{notebook2}:cell_3:3:0: C0411: standard import "operator" should be placed before third party import "IPython.get_ipython" (wrong-import-order)\n'  # noqa: E501
        f"{notebook2}:cell_1:1:0: W0611: Unused randint imported from random (unused-import)\n"
        f"{notebook2}:cell_1:2:0: W0611: Unused get_ipython imported from IPython (unused-import)\n"
        "\n"
        "-----------------------------------\n"
        "Your code has been rated at 5.45/10\n"
        "\n"
    )
    horizontal_bar = "-----------------------------------"
    assert (
        out.replace("\r\n", "\n").split(horizontal_bar)[0]
        == expected_out.split(horizontal_bar)[0]
    )
