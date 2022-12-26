"""mcve"""
import sys
from difflib import unified_diff
from typing import Any, Iterator

RED = "\033[31m"
GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\x1b[0m"


def _print_diff(cell_diff: Iterator[str]) -> None:
    """
    Print diff between cells, colouring as appropriate.
    """
    line_changes = []
    for line in cell_diff:
        if line.startswith("+++") or line.startswith("---"):
            line_changes.append("\033[1;37m" + line + "\033[0m")  # bold white, reset
        elif line.startswith("@@"):
            line_changes.append("\033[36m" + line + "\033[0m")  # cyan, reset
        elif line.startswith("+"):
            line_changes.append("\033[32m" + line + "\033[0m")  # green, reset
        elif line.startswith("-"):
            line_changes.append("\033[31m" + line + "\033[0m")  # red, reset

    sys.stdout.writelines(line_changes + ["\n"])


def test_me(capsys: Any) -> None:
    """mcve"""
    _print_diff(unified_diff("abc", "ab"))
    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1;37m--- \n"
        "\x1b[0m\x1b[1;37m+++ \n"
        "\x1b[0m\x1b[36m@@ -1,3 +1,2 @@\n"
        "\x1b[0m\x1b[31m-c\x1b[0m\n"
    )
    assert out == expected_out
