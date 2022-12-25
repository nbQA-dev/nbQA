"""Tets running local script."""
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_with_subcommand(capsys: "CaptureFixture") -> None:
    """Check subcommand is picked up by module."""
    main(["tests.local_script foo", "."])
    out, _ = capsys.readouterr()
    assert out == "['foo']\n"
