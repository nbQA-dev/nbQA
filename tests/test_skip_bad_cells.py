"""Test the skip bad cells flag."""

import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_cmdline(capsys: "CaptureFixture") -> None:
    """Check running from command-line."""
    file = os.path.join("tests", "invalid_data", "automagic.ipynb")
    main(["black", file, "--nbqa-diff"])
    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {file}\n"
        f"\x1b[0m\x1b[1;37m+++ {file}\n"
        "\x1b[0m\x1b[36m@@ -1,2 +1,2 @@\n"
        "\x1b[0m\x1b[31m-    print('definitely valid')\n"
        '\x1b[0m\x1b[32m+    print("definitely valid")\n'
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected_out


def test_config_file(capsys: "CaptureFixture") -> None:
    """Test setting in config file."""
    file = os.path.join("tests", "invalid_data", "automagic.ipynb")
    main(["black", file, "--nbqa-diff"])
    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {file}\n"
        f"\x1b[0m\x1b[1;37m+++ {file}\n"
        "\x1b[0m\x1b[36m@@ -1,2 +1,2 @@\n"
        "\x1b[0m\x1b[31m-    print('definitely valid')\n"
        '\x1b[0m\x1b[32m+    print("definitely valid")\n'
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected_out
