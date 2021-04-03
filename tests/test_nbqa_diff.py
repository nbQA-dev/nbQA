"""Check --nbqa-diff flag."""

import os
import re
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


SPARKLES = "\N{sparkles}"
SHORTCAKE = "\N{shortcake}"
COLLISION = "\N{collision symbol}"
BROKEN_HEART = "\N{broken heart}"
TESTS_DIR = Path("tests")
TEST_DATA_DIR = TESTS_DIR / "data"

DIRTY_NOTEBOOK = TEST_DATA_DIR / "notebook_for_testing.ipynb"
CLEAN_NOTEBOOK = TEST_DATA_DIR / "clean_notebook.ipynb"


def test_diff_present(capsys: "CaptureFixture") -> None:
    """Test the results on --nbqa-diff on a dirty notebook."""
    with pytest.raises(SystemExit):
        main(["black", str(DIRTY_NOTEBOOK), "--nbqa-diff"])
    out, err = capsys.readouterr()
    err = err.encode("ascii", "backslashreplace").decode()
    expected_out = f"""\x1b[1mCell 2\x1b[0m
------
--- {str(DIRTY_NOTEBOOK)}
+++ {str(DIRTY_NOTEBOOK)}
@@ -12,8 +12,8 @@
     'hello goodbye'
     \"\"\"
 \n\
\x1b[31m-    return 'hello {{}}'.format(name)
\x1b[0m\x1b[32m+    return "hello {{}}".format(name)
\x1b[0m \n\
 \n\
 !ls
\x1b[31m-hello(3)   \n\
\x1b[0m\x1b[32m+hello(3)
\x1b[0m
\x1b[1mCell 4\x1b[0m
------
--- {str(DIRTY_NOTEBOOK)}
+++ {str(DIRTY_NOTEBOOK)}
@@ -1,4 +1,4 @@
 from random import randint
 \n\
 if __debug__:
\x1b[31m-    %time randint(5,10)
\x1b[0m\x1b[32m+    %time randint(5, 10)
\x1b[0m
To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`
"""
    assert out == expected_out
    expected_err = (
        dedent(
            f"""\
            reformatted {str(DIRTY_NOTEBOOK)}
            All done! {SPARKLES} {SHORTCAKE} {SPARKLES}
            1 file reformatted.
            """
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    assert err == expected_err


def test_diff_and_mutate() -> None:
    """
    Check a ValueError is raised if we use both --nbqa-mutate and --nbqa-diff.
    """
    msg = re.escape(
        """\
Cannot use both `--nbqa-diff` and `--nbqa-mutate` flags together!

Use `--nbqa-diff` to preview changes, and `--nbqa-mutate` to apply them.\
"""
    )
    with pytest.raises(ValueError, match=msg):
        main(["black", str(DIRTY_NOTEBOOK), "--nbqa-mutate", "--nbqa-diff"])


def test_invalid_syntax_with_nbqa_diff(capsys: "CaptureFixture") -> None:
    """
    Check that using nbqa-diff when there's invalid syntax doesn't have empty output.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(
        os.path.join("tests", "invalid_data", "assignment_to_literal.ipynb")
    )

    with pytest.raises(SystemExit):
        main(["black", path, "--nbqa-diff"])

    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = (
        (
            f"error: cannot format {path}: "
            "cannot use --safe with this file; failed to parse source file.  AST error message: "
            "can't assign to literal (<unknown>, cell_1:1)\nOh no! "
            f"{COLLISION} {BROKEN_HEART} {COLLISION}\n1 file failed to reformat.\n"
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    # This is required because linux supports emojis
    # so both should have \\ for comparison
    err = err.encode("ascii", "backslashreplace").decode()

    assert expected_out == out
    assert expected_err == err
