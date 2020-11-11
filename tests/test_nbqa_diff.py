from nbqa.__main__ import main
from pathlib import Path
import pytest

TESTS_DIR = Path("tests")
TEST_DATA_DIR = TESTS_DIR / "data"

DIRTY_NOTEBOOK = TEST_DATA_DIR / "notebook_for_testing.ipynb"
CLEAN_NOTEBOOK = TEST_DATA_DIR / "clean_notebook.ipynb"



def test_diff_present(capsys):
    with pytest.raises(SystemExit):
        main(['black', str(DIRTY_NOTEBOOK), '--nbqa-diff'])
    out, err = capsys.readouterr()
    breakpoint()
    assert err == ""


def test_no_diff(capsys):
    with pytest.raises(SystemExit):
        main(['black', str(DIRTY_NOTEBOOK)])
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""