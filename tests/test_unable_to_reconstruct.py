"""Check that :code:`black` works as intended."""

import os

import pytest

from nbqa.__main__ import main


def test_unable_to_reconstruct_message() -> None:
    """Check error message shows if we're unable to reconstruct notebook."""
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))

    message = "Please report a bug at https://github.com/nbQA-dev/nbQA/issues"

    with pytest.raises(RuntimeError, match=message):
        main(["remove_comments", path, "--nbqa-mutate"])
