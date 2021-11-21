"""Check blacken-docs runs."""
import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_blacken_docs(capsys: "CaptureFixture") -> None:
    """
    Check blacken-docs.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    main(["blacken-docs", path, "--nbqa-diff", "--nbqa-md"])
    out, err = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1 +1 @@\n"
        "\x1b[0m\x1b[31m-set(())\n"
        "\x1b[0m\x1b[32m+set()\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    expected_out = (
        "\x1b[1mCell 3\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1,3 +1,3 @@\n"
        "\x1b[0m\x1b[31m-2 +2\n"
        "\x1b[0m\x1b[32m+2 + 2\n"
        "\x1b[0m\n"
        f"{path}: Rewriting...\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    expected_err = ""
    assert out == expected_out
    assert err == expected_err
