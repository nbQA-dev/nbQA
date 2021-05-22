"""Check that :code:`yapf` works as intended."""

import os
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from py._path.local import LocalPath


def test_successive_runs_using_yapf(
    tmpdir: "LocalPath", capsys: "CaptureFixture"
) -> None:
    """Check yapf returns 0 on the second run given a dirty notebook."""
    src_notebook = Path(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    test_notebook = Path(tmpdir) / src_notebook.name
    copyfile(src_notebook, test_notebook)
    main(["yapf", str(test_notebook), "--in-place", "--nbqa-diff"])
    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"--- {str(test_notebook)}\n"
        f"+++ {str(test_notebook)}\n"
        "@@ -16,4 +16,4 @@\n"
        " \n"
        " \n"
        " !ls\n"
        "\x1b[31m-hello(3)   \n"
        "\x1b[0m\x1b[32m+hello(3)\n"
        "\x1b[0m\n"
        "\x1b[1mCell 5\x1b[0m\n"
        "------\n"
        f"--- {str(test_notebook)}\n"
        f"+++ {str(test_notebook)}\n"
        "@@ -2,8 +2,10 @@\n"
        " import sys\n"
        " \n"
        " if __debug__:\n"
        "\x1b[31m-    pretty_print_object = pprint.PrettyPrinter(\n"
        "\x1b[0m\x1b[31m-        indent=4, width=80, stream=sys.stdout, compact=True, depth=5\n"
        "\x1b[0m\x1b[31m-    )\n"
        "\x1b[0m\x1b[32m+    pretty_print_object = pprint.PrettyPrinter(indent=4,\n"
        "\x1b[0m\x1b[32m+                                               width=80,\n"
        "\x1b[0m\x1b[32m+                                               stream=sys.stdout,\n"
        "\x1b[0m\x1b[32m+                                               compact=True,\n"
        "\x1b[0m\x1b[32m+                                               depth=5)\n"
        "\x1b[0m \n"
        ' pretty_print_object.isreadable(["Hello", "World"])\n'
        "\n"
        "To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`\n"
    )
    assert out == expected_out

    main(["yapf", str(test_notebook), "--in-place", "--nbqa-mutate"])
    main(["yapf", str(test_notebook), "--in-place", "--nbqa-diff"])

    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
