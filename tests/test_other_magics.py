"""Check user can check for other magics."""
import os
from pathlib import Path

import pytest

from nbqa.__main__ import main


@pytest.mark.parametrize(
    "magic, expected",
    [
        ("--nbqa-magic=%%custommagic", "cell_2:3:1: F401 'glob' imported but unused"),
        ("--nbqa-magic=%%custommagic,%%anothercustommagic", ""),
    ],
)
def test_cli(magic, expected, capsys):
    path = Path("tests") / "data/notebook_with_other_magics.ipynb"

    with pytest.raises(SystemExit):
        main(["flake8", str(path), magic])

    out, _ = capsys.readouterr()
    if expected:
        expected = f"{str(path.resolve())}:{expected}{os.linesep}"
    breakpoint()
    assert out == expected
