"""Check include-exclude work."""

import re
from pathlib import Path
from textwrap import dedent

import pytest

from nbqa.__main__ import main


def test_cli_files(capsys):
    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--nbqa-files", "^tests/data/notebook_for"])

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"^tests.data.notebook_for", i) for i in out.splitlines()
    )


def test_cli_exclude(capsys):
    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--nbqa-exclude", "^tests/data/notebook_for"])

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"^tests.data.notebook_for", i) is None for i in out.splitlines()
    )


def test_config_files(capsys):

    Path("setup.cfg").write_text(
        dedent(
            """\
        [nbqa.files]
        flake8 = ^tests/data/notebook_for
        """
        )
    )

    with pytest.raises(SystemExit):
        main(["flake8", "tests"])
    Path("setup.cfg").unlink()

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"^tests.data.notebook_for", i) for i in out.splitlines()
    )


def test_config_exclude(capsys):

    Path("setup.cfg").write_text(
        dedent(
            """\
        [nbqa.exclude]
        flake8 = ^tests/data/notebook_for
        """
        )
    )

    with pytest.raises(SystemExit):
        main(["flake8", "tests"])
    Path("setup.cfg").unlink()

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"^tests.data.notebook_for", i) is None for i in out.splitlines()
    )
