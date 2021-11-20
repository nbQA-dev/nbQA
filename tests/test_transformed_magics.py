"""Test the skip_celltags option."""
import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_transformed_magics(capsys: "CaptureFixture") -> None:
    """
    Should ignore cells with transformed magics.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.join("tests", "data", "transformed_magics.ipynb")
    main(["black", path, "--nbqa-diff"])
    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1 +1 @@\n"
        "\x1b[0m\x1b[31m-2+2\n"
        "\x1b[0m\x1b[32m+2 + 2\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected_out
