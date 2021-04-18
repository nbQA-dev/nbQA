"""Check include-exclude work."""

import re
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING


from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_cli_files(capsys: "CaptureFixture") -> None:
    """
    Test --nbqa-files is picked up correctly.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    main(["flake8", "tests", "--nbqa-files", "^tests/data/notebook_for"])

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"tests.data.notebook_for", i) for i in out.splitlines()
    )


def test_cli_exclude(capsys: "CaptureFixture") -> None:
    """
    Test --nbqa-exclude is picked up correctly.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    main(["flake8", "tests", "--nbqa-exclude", "^tests/data/notebook_for"])

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"^tests.data.notebook_for", i) is None for i in out.splitlines()
    )


def test_config_files(capsys: "CaptureFixture") -> None:
    """
    Test [nbqa.files] config is picked up correctly.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("setup.cfg").write_text(
        dedent(
            """\
        [nbqa.files]
        flake8 = ^tests/data/notebook_for
        """
        )
    )

    main(["flake8", "tests"])
    Path("setup.cfg").unlink()

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"tests.data.notebook_for", i) for i in out.splitlines()
    )


def test_config_exclude(capsys: "CaptureFixture") -> None:
    """
    Test [nbqa.exclude] config is picked up correctly.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("setup.cfg").write_text(
        dedent(
            """\
        [nbqa.exclude]
        flake8 = ^tests/data/notebook_for
        """
        )
    )

    main(["flake8", "tests"])
    Path("setup.cfg").unlink()

    out, _ = capsys.readouterr()
    assert out and all(
        re.search(r"^tests.data.notebook_for", i) is None for i in out.splitlines()
    )
