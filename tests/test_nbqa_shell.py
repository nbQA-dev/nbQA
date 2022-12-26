"""Ensure the --nbqa-shell flag correctly calls the underlying command."""
import os
import sys
from shutil import which
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
    expected_run = [which("black"), path]
    main(args)
    out, err = capsys.readouterr()
    received = err.strip()
    expected = _message(args=expected_run)  # type:ignore[arg-type]
    assert (
        received == expected
    ), f"nbqa called unexpected `{received}` instead of `{expected}` for args `{args}`"
    assert out == "", f"No stdout expected. Received `{out}`"


def test_nbqa_not_shell(monkeypatch: MonkeyPatch, capsys: CaptureFixture) -> None:
    """Check nbqa without --nbqa-shell command call."""
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    monkeypatch.setattr("subprocess.run", subprocess_run)

    args = ["black", path]
    expected_run = [sys.executable, "-m", "black", path]
    main(args)
    out, err = capsys.readouterr()
    received = err.strip()
    expected = _message(args=expected_run)
    assert (
        received == expected
    ), f"nbqa called unexpected `{received}` instead of `{expected}` for args `{args}`"
    assert out == "", f"No stdout expected. Received `{out}`"


def test_nbqa_shell_not_found(monkeypatch: MonkeyPatch) -> None:
    """Check --nbqa-shell command call with inexistend command."""
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    monkeypatch.setattr("subprocess.run", subprocess_run)

    args = ["some-fictional-command", "--nbqa-shell", path]
    msg = "\x1b\\[1mnbqa was unable to find some-fictional-command.\x1b\\[0m"
    with pytest.raises(CommandNotFoundError, match=msg):
        main(args)
