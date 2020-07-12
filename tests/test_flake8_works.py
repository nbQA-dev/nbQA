import difflib
import shutil
from pathlib import Path

from nbqa.__main__ import main


def test_flake8_works(tmpdir, capsys):
    shutil.copy(
        str(Path("tests/data") / "test_notebook.ipynb"),
        str(Path(tmpdir) / "test_notebook.ipynb"),
    )
    with open(Path("tests/data") / "test_notebook.ipynb", "r") as handle:
        before = handle.readlines()
    main("flake8")
    with open(Path("tests/data") / "test_notebook.ipynb", "r") as handle:
        after = handle.readlines()

    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    (Path("tests/data") / "test_notebook.ipynb").unlink()

    shutil.copy(
        str(Path(tmpdir) / "test_notebook.ipynb"),
        str(Path("tests/data") / "test_notebook.ipynb"),
    )

    assert result == expected

    out, err = capsys.readouterr()

    expected_out = (
        "test_notebook.ipynb:cell_1:1:1: F401 'pandas as pd' imported but unused\n"
        "test_notebook.ipynb:cell_1:3:1: F401 'numpy as np' imported but unused\n"
        "test_notebook.ipynb:cell_1:5:1: F401 'os' imported but unused\n"
        "test_notebook.ipynb:cell_3:2:1: E302 expected 2 blank lines, found 1\n\n"
    )

    assert out == expected_out
