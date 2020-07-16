from pathlib import Path

from nbqa.__main__ import _create_blank_init_files


def test_create_blank_init_files(tmpdir):
    """
    Check that if a notebook is in current working directory then no init file is made.
    """
    _create_blank_init_files(Path("some_notebook.ipynb"), tmpdir)
    result = list(Path(tmpdir).rglob("__init__.py"))
    assert result == []
