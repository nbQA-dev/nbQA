"""Ensure the --nbqa-shell flag correctly calls the underlying command."""
import os
import sys
from subprocess import CompletedProcess
from typing import List

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from nbqa.__main__ import CommandNotFoundError, main


def _message(args: List[str]) -> str:
    return f"I would have run `{args[:-1]}`"


def subprocess_run(args: List[str], *_, **__):  # type: ignore
    """Mock subprocess run to print and return ok."""
    print(_message(args=args), file=sys.stderr)
    return CompletedProcess(args, 0, b"", b"")


def test_nbqa_shell(monkeypatch: MonkeyPatch, capsys: CaptureFixture) -> None:
    """Check nbqa shell command call."""
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    monkeypatch.setattr("subprocess.run", subprocess_run)

    args = ["black", "--nbqa-shell", path]
    main(args)
    out, err = capsys.readouterr()
    received = err.strip()
    black_executable = sys.executable.replace("python", "black")
    expected = (
        f"I would have run `['{sys.executable}', '-m', 'autopep8', '--select=E3', '--in-place']`\n"
        f"I would have run `['{black_executable}']`"
    )
    assert received == expected
    assert out == ""


def test_nbqa_not_shell(monkeypatch: MonkeyPatch, capsys: CaptureFixture) -> None:
    """Check nbqa without --nbqa-shell command call."""
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    monkeypatch.setattr("subprocess.run", subprocess_run)

    args = ["black", path]
    main(args)
    out, err = capsys.readouterr()
    received = err.strip()
    expected = (
        f"I would have run `['{sys.executable}', '-m', 'autopep8', '--select=E3', '--in-place']`\n"
        f"I would have run `['{sys.executable}', '-m', 'black']`"
    )
    assert received == expected
    assert out == ""


def test_nbqa_shell_not_found(monkeypatch: MonkeyPatch) -> None:
    """Check --nbqa-shell command call with inexistend command."""
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    monkeypatch.setattr("subprocess.run", subprocess_run)

    args = ["some-fictional-command", "--nbqa-shell", path]
    msg = "\x1b\\[1mnbqa was unable to find some-fictional-command.\x1b\\[0m"
    with pytest.raises(CommandNotFoundError, match=msg):
        main(args)


@pytest.mark.skipif(sys.platform != "linux", reason="needs grep")
def test_grep(capsys: CaptureFixture) -> None:
    """Check grep with string works."""
    main(["grep 'import pandas'", ".", "--nbqa-shell"])
    out, _ = capsys.readouterr()
    assert out == "tests/data/notebook_for_autoflake.ipynb:import pandas as pd\n"
