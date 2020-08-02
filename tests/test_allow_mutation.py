"""Check that :code:`black` works as intended."""

import os
from textwrap import dedent

import pytest

from nbqa.__main__ import main


def test_allow_mutation() -> None:
    """Check black, without --nbqa-mutate, errors."""
    # check diff
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    msg = dedent(
        f"""\
        Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path])
    msg = dedent(
        f"""\
        Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --line-length 96 --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--line-length", "96"])
    msg = dedent(
        f"""\
        Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --nbqa-config=setup.cfg --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--nbqa-config=setup.cfg"])
    msg = dedent(
        f"""\
        Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

            nbqa black {path} --nbqa-preserve-init --nbqa-mutate
        """
    )
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--nbqa-preserve-init"])
