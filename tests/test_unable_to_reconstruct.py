"""Check that :code:`black` works as intended."""

import os
from textwrap import dedent

import pytest

from nbqa.__main__ import main


def test_unable_to_reconstruct_message() -> None:
    """
    Check black works. Should only reformat code cells.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))

    message = dedent(
        f"""
        😭 Error reconstructing {path} 😭

        Please report a bug at https://github.com/nbQA-dev/nbQA/issues 🙏
        """
    )

    with pytest.raises(RuntimeError, match=message):
        main(["remove_comments", path, "--nbqa-mutate"])
