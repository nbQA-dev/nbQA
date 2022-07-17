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
    return CompletedProcess(args, 0, "", "")


def test_nbqa_shell(monkeypatch: MonkeyPatch, capsys: CaptureFixture) -> None:
    """Check nbqa shell command call."""
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    monkeypatch.setattr("subprocess.run", subprocess_run)

    args = ["black", "--nbqa-shell", path]
    expected_run = ["black", path]
    main(args)
    out, err = capsys.readouterr()
    received = err.strip()
    expected = _message(args=expected_run)
    assert (
        received == expected
    ), f"nbqa called unexpected `{received}` instead of `{expected}` for args `{args}`"
    assert out == "", f"No stdout expected. Received `{out}`"


def test_nbqa_shell_pyproject_toml(capsys: CaptureFixture) -> None:
    """Check nbqa shell command call when set in pyproject.toml"""
    with open("pyproject.toml", "w", encoding="utf-8") as handle:
        handle.write("[tool.nbqa.shell]\nflake8heavened = true\n")
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")

    args = ["flake8heavened", path]
    main(args)
    out, _ = capsys.readouterr()
    expected_out = (
        f"{path}:\x1b[32m32\x1b[0m:\x1b[32m1\x1b[0m: \x1b[31mE\x1b[0m\x1b[36m402\x1b[0m module level import not at top of file\x1b[35m [pycodestyle]\x1b[0m\n"  # noqa: E501
        f"{path}:\x1b[32m39\x1b[0m:\x1b[32m1\x1b[0m: \x1b[31mE\x1b[0m\x1b[36m402\x1b[0m module level import not at top of file\x1b[35m [pycodestyle]\x1b[0m\n"  # noqa: E501
        f"{path}:\x1b[32m40\x1b[0m:\x1b[32m1\x1b[0m: \x1b[31mE\x1b[0m\x1b[36m402\x1b[0m module level import not at top of file\x1b[35m [pycodestyle]\x1b[0m\n"  # noqa: E501
        f"{path}:\x1b[32m28\x1b[0m:\x1b[32m9\x1b[0m: \x1b[33mW\x1b[0m\x1b[36m291\x1b[0m trailing whitespace\x1b[35m [pycodestyle]\x1b[0m\n"  # noqa: E501
        f"{path}:\x1b[32m2\x1b[0m:\x1b[32m1\x1b[0m: \x1b[31mF\x1b[0m\x1b[36m401\x1b[0m \x1b[33m'os'\x1b[0m imported but unused\x1b[35m [pyflakes]\x1b[0m\n"  # noqa: E501
        f"{path}:\x1b[32m4\x1b[0m:\x1b[32m1\x1b[0m: \x1b[31mF\x1b[0m\x1b[36m401\x1b[0m \x1b[33m'glob'\x1b[0m imported but unused\x1b[35m [pyflakes]\x1b[0m\n"  # noqa: E501
        f"{path}:\x1b[32m6\x1b[0m:\x1b[32m1\x1b[0m: \x1b[31mF\x1b[0m\x1b[36m401\x1b[0m \x1b[33m'nbqa'\x1b[0m imported but unused\x1b[35m [pyflakes]\x1b[0m\n"  # noqa: E501
        f"{path}:\x1b[32m32\x1b[0m:\x1b[32m1\x1b[0m: \x1b[31mF\x1b[0m\x1b[36m401\x1b[0m \x1b[33m'random.randint'\x1b[0m imported but unused\x1b[35m [pyflakes]\x1b[0m\n"  # noqa: E501
    )
    assert out == expected_out


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
