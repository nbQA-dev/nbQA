import difflib
import shutil
from pathlib import Path

from nbqa.__main__ import main


def test_black_works(tmpdir):
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
    expected = None
    (Path("tests/data") / "test_notebook.ipynb").unlink()

    shutil.copy(
        str(Path(tmpdir) / "test_notebook.ipynb"),
        str(Path("tests/data") / "test_notebook.ipynb"),
    )
    breakpoint()
    assert result == expected
