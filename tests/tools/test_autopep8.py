"""Check that :code:`autopep8` works as intended."""

import os
import sys
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

pytest.mark.skipif(
    sys.version_info >= (3, 11),
    reason="deprecation warning needs sorting out in autopep8",
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from py._path.local import LocalPath


def test_successive_runs_using_autopep8(
    tmpdir: "LocalPath", capsys: "CaptureFixture"
) -> None:
    """Check autopep8 returns 0 on the second run given a dirty notebook."""
    src_notebook = Path(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    test_notebook = Path(tmpdir) / src_notebook.name
    copyfile(src_notebook, test_notebook)
    main(["autopep8", str(test_notebook), "-i", "--nbqa-diff"])
    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {str(test_notebook)}\n"
        f"\x1b[0m\x1b[1;37m+++ {str(test_notebook)}\n"
        "\x1b[0m\x1b[36m@@ -1,3 +1,6 @@\n"
        "\x1b[0m\x1b[32m+import sys\n"
        "\x1b[0m\x1b[32m+import pprint\n"
        "\x1b[0m\x1b[32m+from random import randint\n"
        "\x1b[0m\n"
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {str(test_notebook)}\n"
        f"\x1b[0m\x1b[1;37m+++ {str(test_notebook)}\n"
        "\x1b[0m\x1b[36m@@ -16,4 +16,4 @@\n"
        "\x1b[0m\x1b[31m-hello(3)   \n"
        "\x1b[0m\x1b[32m+hello(3)\n"
        "\x1b[0m\n"
        "\x1b[1mCell 4\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {str(test_notebook)}\n"
        f"\x1b[0m\x1b[1;37m+++ {str(test_notebook)}\n"
        "\x1b[0m\x1b[36m@@ -1,4 +1,2 @@\n"
        "\x1b[0m\x1b[31m-from random import randint\n"
        "\x1b[0m\x1b[31m-\n"
        "\x1b[0m\n"
        "\x1b[1mCell 5\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {str(test_notebook)}\n"
        f"\x1b[0m\x1b[1;37m+++ {str(test_notebook)}\n"
        "\x1b[0m\x1b[36m@@ -1,6 +1,3 @@\n"
        "\x1b[0m\x1b[31m-import pprint\n"
        "\x1b[0m\x1b[31m-import sys\n"
        "\x1b[0m\x1b[31m-\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected_out

    main(["autopep8", str(test_notebook), "-i"])
    main(["autopep8", str(test_notebook), "-i", "--nbqa-diff"])

    out, err = capsys.readouterr()
    assert out == "Notebook(s) would be left unchanged\n"
    assert err == ""
