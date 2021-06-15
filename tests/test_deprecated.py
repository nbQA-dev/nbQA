"""Test deprecations."""
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_deprecated(capsys: "CaptureFixture") -> None:
    """Test deprecation errors."""
    with pytest.raises(SystemExit):
        main(["flake8", ".", "--nbqa-skip-bad-cells"])
    out, err = capsys.readouterr()
    assert out == ""
    assert err == (
        "Flag --nbqa-skip-bad-cells was deprecated in 0.13.0\n"
        "Cells with invalid syntax are now skipped by default\n"
    )
