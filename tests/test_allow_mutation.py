"""Check that :code:`black` works as intended."""

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
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    msg = dedent(
        f"""\
        💥 Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path])
    msg = dedent(
        f"""\
        💥 Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --line-length 96 --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--line-length", "96"])
    msg = dedent(
        f"""\
        💥 Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --nbqa-config=setup.cfg --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--nbqa-config=setup.cfg"])
    msg = dedent(
        f"""\
        💥 Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --nbqa-preserve-init --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--nbqa-preserve-init"])
