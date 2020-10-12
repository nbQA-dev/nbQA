"""Check that return code from third-party tool is preserved."""

import os
import subprocess

DIRTY_NOTEBOOK = os.path.join("tests", "data", "notebook_for_testing.ipynb")
CLEAN_NOTEBOOK = os.path.join("tests", "data", "clean_notebook.ipynb")
NOTEBOOK_WITH_CELL_AFTER_DEF = os.path.join(
    "tests", "data", "notebook_with_cell_after_def.ipynb"
)


def test_flake8_return_code() -> None:
    """Check flake8 returns 0 if it passes, 1 otherwise."""
    output = subprocess.run(["nbqa", "flake8", DIRTY_NOTEBOOK])
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(["nbqa", "flake8", CLEAN_NOTEBOOK])
    result = output.returncode
    expected = 0
    assert result == expected


def test_pylint_return_code() -> None:
    """Check pylint returns 0 if it passes, 1 otherwise."""
    output = subprocess.run(["nbqa", "pylint", DIRTY_NOTEBOOK])
    assert output.returncode == 1

    output = subprocess.run(["nbqa", "pylint", CLEAN_NOTEBOOK, "--disable=C0114"])
    assert output.returncode == 0


def test_black_return_code() -> None:
    """Check black returns 0 if it passes, 1 otherwise."""
    output = subprocess.run(["nbqa", "black", DIRTY_NOTEBOOK, "--check"])
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(["nbqa", "black", "--check", CLEAN_NOTEBOOK])
    result = output.returncode
    expected = 0
    assert result == expected

    output = subprocess.run(["nbqa", "black", "--check", NOTEBOOK_WITH_CELL_AFTER_DEF])
    result = output.returncode
    expected = 0
    assert result == expected

    output = subprocess.run(["nbqa", "black", "--check", "tests"])
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(["nbqa", "black", CLEAN_NOTEBOOK, "--check", "-l", "1"])
    result = output.returncode
    expected = 1
    assert result == expected
