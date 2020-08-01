"""Check that return code from third-party tool is preserved."""

import os
import subprocess

DIRTY_NOTEBOOK = os.path.join("tests", "data", "notebook_for_testing.ipynb",)
CLEAN_NOTEBOOK = os.path.join("tests", "data", "clean_notebook.ipynb",)


def test_flake8_return_code() -> None:
    """Check flake8 returns 0 if it passes, 1 otherwise."""
    output = subprocess.run(["python", "-m", "nbqa", "flake8", DIRTY_NOTEBOOK])
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(["python", "-m", "nbqa", "flake8", CLEAN_NOTEBOOK])
    result = output.returncode
    expected = 0
    assert result == expected


def test_black_return_code() -> None:
    """Check black returns 0 if it passes, 1 otherwise."""
    output = subprocess.run(
        ["python", "-m", "nbqa", "black", DIRTY_NOTEBOOK, "--check"]
    )
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(
        ["python", "-m", "nbqa", "black", "--check", CLEAN_NOTEBOOK]
    )
    result = output.returncode
    expected = 0
    assert result == expected

    output = subprocess.run(["python", "-m", "nbqa", "black", "--check", "tests"])
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(
        ["python", "-m", "nbqa", "black", CLEAN_NOTEBOOK, "--check", "-l", "1"]
    )
    result = output.returncode
    expected = 1
    assert result == expected
