"""Check what happens if cell separator appears in notebook."""

import os

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from nbqa.__main__ import main


@pytest.mark.skip(reason="too slow - TODO how to re-enable / speedup?")
def test_hash_collision(monkeypatch: MonkeyPatch, capsys: CaptureFixture) -> None:
    """Check hash collision error message."""
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    monkeypatch.setattr("nbqa.save_code_source.CODE_SEPARATOR", "pprint\n")
    main(["flake8", path])
    _, err = capsys.readouterr()
    assert (
        "Extremely rare hash collision occurred - please re-run nbQA to fix this" in err
    )
