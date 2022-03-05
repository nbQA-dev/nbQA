"""Check --nbqa-diff flag."""

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

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
    main(["black", str(DIRTY_NOTEBOOK), "--nbqa-diff"])
    out, err = capsys.readouterr()
    err = err.encode("ascii", "backslashreplace").decode()
    expected_out = (
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {str(DIRTY_NOTEBOOK)}\n"
        f"\x1b[0m\x1b[1;37m+++ {str(DIRTY_NOTEBOOK)}\n"
        "\x1b[0m\x1b[36m@@ -12,8 +12,8 @@\n"
        "\x1b[0m\x1b[31m-    return 'hello {}'.format(name)\n"
        '\x1b[0m\x1b[32m+    return "hello {}".format(name)\n'
        "\x1b[0m\x1b[31m-hello(3)   \n"
        "\x1b[0m\x1b[32m+hello(3)\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
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


def test_invalid_syntax_with_nbqa_diff(capsys: "CaptureFixture") -> None:
    """
    Check that using nbqa-diff when there's invalid syntax doesn't have empty output.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.join("tests", "invalid_data", "assignment_to_literal.ipynb")

    main(["black", os.path.abspath(path), "--nbqa-diff", "--nbqa-dont-skip-bad-cells"])

    out, err = capsys.readouterr()
    expected_out = "Notebook(s) would be left unchanged\n"
    expected_err = (
        (f"{COLLISION} {BROKEN_HEART} {COLLISION}\n1 file failed to reformat.\n")
        .encode("ascii", "backslashreplace")
        .decode()
    )
    # This is required because linux supports emojis
    # so both should have \\ for comparison
    err = err.encode("ascii", "backslashreplace").decode()

    assert expected_out == out
    assert expected_err in err
