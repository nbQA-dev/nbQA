"""Check that :code:`black` works as intended."""

import difflib
import os
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from pathlib import Path


def test_allow_mutation(tmp_notebook_for_testing: "Path",) -> None:
    """
    Check black, without --nbqa-mutate, errors and doesn't modify notebook.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    msg = dedent(
        """\
        💥 Mutation detected, will not reformat!

        To allow for mutation, please use the `--nbqa-mutate` flag, e.g.

        ```
        nbqa black my_notebook.ipynb --nbqa-mutate
        ```
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path])
    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = ""
    assert result == expected
