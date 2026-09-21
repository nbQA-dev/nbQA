"""Check that return code from third-party tool is preserved."""

import subprocess
from functools import partial
from pathlib import Path
from typing import Sequence
from unittest import mock

from nbqa import __main__ as nbqa_main
from nbqa.output_parser import Output

TESTS_DIR = Path("tests")
TEST_DATA_DIR = TESTS_DIR / "data"
DIRTY_NOTEBOOK = TEST_DATA_DIR / "notebook_for_testing.ipynb"
CLEAN_NOTEBOOK = TEST_DATA_DIR / "clean_notebook.ipynb"
EMPTY_NOTEBOOK = TEST_DATA_DIR / "empty_notebook.ipynb"
INVALID_SYNTAX_NOTEBOOK = TESTS_DIR / "invalid_data" / "invalid_syntax.ipynb"

# Interpret the below constants in the same context as that of pre-commit tool
# Success indicates the QA tool reported no issues.
PASSED = 0
FAILED = 1


def _run_nbqa_with(command: str, notebooks: Sequence[Path], *args: str) -> int:
    """Run nbqa with the QA tool specified by command parameter."""
    notebook_paths = map(str, notebooks)
    output = subprocess.run(["nbqa", command, *notebook_paths, *args])
    return output.returncode


def test_flake8_return_code() -> None:
    """Check flake8 returns 0 if it passes, 1 otherwise."""
    flake8_runner = partial(_run_nbqa_with, "flake8")
    assert flake8_runner([DIRTY_NOTEBOOK]) != PASSED
    assert flake8_runner([CLEAN_NOTEBOOK]) == PASSED


def test_autoflake_return_code() -> None:
    """Check flake8 returns 0 if it passes, 1 otherwise."""
    autoflake_options = [
        "--check",
        "--expand-star-imports",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
    ]
    autoflake_runner = partial(_run_nbqa_with, "autoflake")
    assert autoflake_runner([CLEAN_NOTEBOOK], *autoflake_options) == PASSED
    assert (
        autoflake_runner(
            [TEST_DATA_DIR / "notebook_for_autoflake.ipynb"], *autoflake_options
        )
        != PASSED
    )


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
        EMPTY_NOTEBOOK,
    ]
    assert black_runner(clean_notebooks, "--check") == PASSED

    # This is to test if the tool ran on all the notebooks in a given directory
    assert black_runner([TESTS_DIR], "--check") != PASSED


def test_check_ast_return_code() -> None:
    """Check check-ast returns 0 if it passes, 1 otherwise."""
    check_ast_runner = partial(_run_nbqa_with, "pre_commit_hooks.check_ast")

    assert check_ast_runner([DIRTY_NOTEBOOK]) == PASSED
    assert (
        check_ast_runner([INVALID_SYNTAX_NOTEBOOK], "--nbqa-dont-skip-bad-cells")
        != PASSED
    )


def test_return_code_survives_unchanged_notebook() -> None:
    """Tool reported an issue, so nbQA must not report success.

    See https://github.com/nbQA-dev/nbQA/issues/872: ``ruff check --fix`` fixes
    some violations, leaves others, and exits 1. If nbQA's round-trip happens to
    leave the notebook unchanged, that 1 must still reach the caller.
    """
    reported = Output("clean_notebook.ipynb:cell_1:1:1: F821 Undefined name `x`\n", "")
    with mock.patch.object(
        nbqa_main, "_run_command", return_value=(reported, FAILED, True)
    ), mock.patch.object(
        nbqa_main, "_post_process_notebooks", return_value=(False, reported)
    ):
        assert nbqa_main.main(["flake8", str(CLEAN_NOTEBOOK)]) == FAILED


def test_silent_tool_exit_code_is_still_reset() -> None:
    """Tool said nothing, so its exit code was only about rewriting files."""
    silent = Output("", "")
    with mock.patch.object(
        nbqa_main, "_run_command", return_value=(silent, FAILED, True)
    ), mock.patch.object(
        nbqa_main, "_post_process_notebooks", return_value=(False, silent)
    ):
        assert nbqa_main.main(["flake8", str(CLEAN_NOTEBOOK)]) == PASSED


def test_success_stays_success_for_unchanged_notebook() -> None:
    """``black`` reformatted the temporary file but the notebook is unchanged."""
    reformatted = Output("", "reformatted clean_notebook.ipynb\n")
    with mock.patch.object(
        nbqa_main, "_run_command", return_value=(reformatted, PASSED, True)
    ), mock.patch.object(
        nbqa_main, "_post_process_notebooks", return_value=(False, reformatted)
    ):
        assert nbqa_main.main(["black", str(CLEAN_NOTEBOOK)]) == PASSED
