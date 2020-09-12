"""Check user can check for other magics."""
import os
from pathlib import Path

import pytest

from nbqa.__main__ import main


def test_cli(capsys):
    path = Path("tests") / "data/notebook_with_other_magics.ipynb"

    with pytest.raises(SystemExit):
        main(["flake8", str(path), "--nbqa-magic=%%custommagic"])

    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
