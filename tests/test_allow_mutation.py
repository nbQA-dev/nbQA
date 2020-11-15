"""Check that :code:`black` won't reformat without --nbqa-mutate."""

import os
from textwrap import dedent

import pytest

from nbqa.__main__ import main


def test_allow_mutation() -> None:
    """Check black, without --nbqa-mutate, errors."""
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    msg = dedent(
        """\
        \x1b[1mMutation detected, will not reformat! Please use the `--nbqa-mutate` flag, e.g.:\x1b[0m

            nbqa black notebook.ipynb --nbqa-mutate

        or, to only preview changes, use the `--nbqa-diff` flag, e.g.:

            nbqa black notebook.ipynb --nbqa-diff
        """
    )

    with pytest.raises(SystemExit) as excinfo:
        main(["black", path])
    assert msg == str(excinfo.value)

    with pytest.raises(SystemExit) as excinfo:
        main(["black", path, "--line-length", "96"])
    assert msg == str(excinfo.value)

    with pytest.raises(SystemExit) as excinfo:
        main(["black", path, "--nbqa-config=tox.ini"])
    assert msg == str(excinfo.value)
