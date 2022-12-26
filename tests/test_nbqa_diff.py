"""Check --nbqa-diff flag."""

import os
import re
from pathlib import Path
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
    print("*** out")
    print(out)
    # expected_out = (
    #     "\x1b[1mCell 2\x1b[0m\n"
    #     "------\n"
    #     f"\x1b[1;37m--- {str(DIRTY_NOTEBOOK)}\n"
    #     f"\x1b[0m\x1b[1;37m+++ {str(DIRTY_NOTEBOOK)}\n"
    #     "\x1b[0m\x1b[36m@@ -12,8 +12,8 @@\n"
    #     "\x1b[0m\x1b[31m-    return 'hello {}'.format(name)\n"
    #     '\x1b[0m\x1b[32m+    return "hello {}".format(name)\n'
    #     "\x1b[0m\x1b[31m-hello(3)   \n"
    #     "\x1b[0m\x1b[32m+hello(3)\n"
    #     "\x1b[0m\n"
    #     "To apply these changes, remove the `--nbqa-diff` flag\n"
    # )
    expected_err = (
        rf"reformatted {str(DIRTY_NOTEBOOK)}\n"
        "\n"
        r"All done! .*\n"
        "1 file reformatted.\n"
    )
    assert out == ""
    assert re.search(expected_err, err) is not None


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
    expected_err = "failed to reformat"

    assert expected_out == out
    assert re.search(expected_err, err) is not None
