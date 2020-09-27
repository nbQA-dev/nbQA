"""Check that nbqa still works even if __init__ files aren't present."""

import os
import subprocess
from pathlib import Path

CLEAN_NOTEBOOK = os.path.join("tests", "data", "clean_notebook.ipynb")


def test_no_inits() -> None:
    """Check flake8 works even if notebook is in nested folder without inits."""
    Path("tests/__init__.py").unlink()
    Path("tests/data/__init__.py").unlink()
    output = subprocess.run(["nbqa", "flake8", CLEAN_NOTEBOOK])
    result = output.returncode
    expected = 0
    assert result == expected

    Path("tests/__init__.py").touch()
    Path("tests/data/__init__.py").touch()
