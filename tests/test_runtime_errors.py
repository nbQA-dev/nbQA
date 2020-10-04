"""Check that users are encouraged to report bugs if reconstructing notebook fails."""

import os
from pathlib import Path

import pytest

from nbqa.__main__ import main


def test_unable_to_reconstruct_message() -> None:
    """Check error message shows if we're unable to reconstruct notebook."""
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    message = f"Error reconstructing {path}"
    with pytest.raises(RuntimeError, match=message):
        main(["remove_comments", path, "--nbqa-mutate"])


def test_unable_to_parse() -> None:
    """Check error message shows if we're unable to parse notebook."""
    path = Path("tests") / "data/invalid_notebook.ipynb"
    path.write_text("foo")
    message = f"Error parsing {str(path)}"
    with pytest.raises(RuntimeError, match=message):
        main(["flake8", str(path), "--nbqa-mutate"])
    path.unlink()
