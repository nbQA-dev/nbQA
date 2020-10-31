"""Check that return code from third-party tool is preserved."""

import subprocess
from functools import partial
from pathlib import Path
from typing import List

TESTS_DIR = Path("tests")
TEST_DATA_DIR = TESTS_DIR / "data"
DIRTY_NOTEBOOK = TEST_DATA_DIR / "notebook_for_testing.ipynb"
CLEAN_NOTEBOOK = TEST_DATA_DIR / "clean_notebook.ipynb"

# Interpret the below constants in the same context as that of pre-commit tool
# Success indicates the QA tool reported no issues.
PASSED = 0


def _run_nbqa_with(command: str, notebooks: List[Path], *args: str) -> int:
    """Run nbqa with the QA tool specified by command parameter."""
    notebook_paths = map(str, notebooks)
    output = subprocess.run(["nbqa", command, *notebook_paths, *args])
    return output.returncode


def test_flake8_return_code() -> None:
    """Check flake8 returns 0 if it passes, 1 otherwise."""
    flake8_runner = partial(_run_nbqa_with, "flake8")
    assert flake8_runner([DIRTY_NOTEBOOK]) != PASSED
    assert flake8_runner([CLEAN_NOTEBOOK]) == PASSED


def test_pylint_return_code() -> None:
    """Check pylint returns 0 if it passes, 20 otherwise."""
    pylint_runner = partial(_run_nbqa_with, "pylint")
    assert pylint_runner([DIRTY_NOTEBOOK]) != PASSED
    assert pylint_runner([CLEAN_NOTEBOOK], "--disable=C0114") == PASSED


def test_black_return_code() -> None:
    """Check black returns 0 if it passes, 1 otherwise."""
    black_runner = partial(_run_nbqa_with, "black")

    assert black_runner([DIRTY_NOTEBOOK], "--check") != PASSED

    clean_notebooks = [
        CLEAN_NOTEBOOK,
        TEST_DATA_DIR / "notebook_with_cell_after_def.ipynb",
        TEST_DATA_DIR / "clean_notebook_with_trailing_semicolon.ipynb",
    ]
    assert black_runner(clean_notebooks, "--check") == PASSED

    # This is to test if the tool ran on all the notebooks in a given directory
    assert black_runner([TESTS_DIR], "--check") != PASSED
