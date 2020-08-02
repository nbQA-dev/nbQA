"""Check that :code:`black` won't reformat without --nbqa-mutate."""

import os

import pytest

from nbqa.__main__ import main


def test_allow_mutation() -> None:
    """Check black, without --nbqa-mutate, errors."""
    # check diff
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    msg = f"nbqa black {path} --nbqa-mutate"
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path])
    msg = f"nbqa black {path} --line-length 96 --nbqa-mutate"
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--line-length", "96"])
    msg = f"nbqa black {path} --nbqa-config=setup.cfg --nbqa-mutate"
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--nbqa-config=setup.cfg"])
    msg = f"nbqa black {path} --nbqa-preserve-init --nbqa-mutate"
    with pytest.raises(
        SystemExit, match=msg,
    ):
        main(["black", path, "--nbqa-preserve-init"])
