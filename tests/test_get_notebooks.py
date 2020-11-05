"""Check function which lists notebooks in directory."""

from pathlib import Path
from typing import TYPE_CHECKING

from nbqa.__main__ import _get_notebooks

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_get_notebooks(monkeypatch: "MonkeyPatch"):
    """
    Check that unwanted directories are excluded.

    Parameters
    ----------
    monkeypatch
        Pytest fixture, we use it to override ``PYTHONPATH``.

    """
    result = list(_get_notebooks("tests"))
    assert Path("tests") / "data/clean_notebook.ipynb" in result

    monkeypatch.setattr("nbqa.__main__.EXCLUDES", r"/(data)/")
    result = list(_get_notebooks("tests"))
    assert not result
