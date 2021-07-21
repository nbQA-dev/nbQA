"""Test deprecations."""
import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_deprecated(capsys: "CaptureFixture") -> None:
    """Test deprecation errors."""
    path = os.path.join("tests", "data", "clean_notebook.ipynb")
    main(["flake8", path, "--nbqa-skip-bad-cells"])
    _, err = capsys.readouterr()
    assert err == (
        "Flag --nbqa-skip-bad-cells was deprecated in 0.13.0\n"
        "Cells with invalid syntax are now skipped by default\n"
    )
