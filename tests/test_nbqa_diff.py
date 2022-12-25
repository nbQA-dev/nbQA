"""Check --nbqa-diff flag."""
import re
from pathlib import Path
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


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
        rf"reformatted {re.escape(str(DIRTY_NOTEBOOK))}\n"
        r"\n"
        r"All done! .*\n"
        r"1 file reformatted.\n"
    )
    assert re.search(expected_err, err)
