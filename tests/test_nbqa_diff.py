"""Check --nbqa-diff flag."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture

import subprocess

SPARKLES = "\N{sparkles}"
SHORTCAKE = "\N{shortcake}"
COLLISION = "\N{collision symbol}"
BROKEN_HEART = "\N{broken heart}"
TESTS_DIR = Path("tests")
TEST_DATA_DIR = TESTS_DIR / "data"

DIRTY_NOTEBOOK = TEST_DATA_DIR / "notebook_for_testing.ipynb"
CLEAN_NOTEBOOK = TEST_DATA_DIR / "clean_notebook.ipynb"


def test_diff_present(capsys: "CaptureFixture") -> None:
    """Test the results on --nbqa-diff on a dirty notebook."""
    # main(["black", os.path.join("tests", "data", "notebook_for_testing.ipynb")])
    subprocess.run(["black", "f.py"])

    out, err = capsys.readouterr()
    assert out is not None
    assert err is not None
