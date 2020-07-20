import os
from pathlib import Path

from nbqa.__main__ import _create_blank_init_files


def test_create_blank_init_files(tmpdir):
    """
    Check that if a notebook is in current working directory then no init file is made.
    """
    _create_blank_init_files(
        Path(os.path.join("tests", "data", "notebook_for_testing.ipynb")), tmpdir
    )
    result = list(Path(tmpdir).rglob("__init__.py"))
    expected = [
        Path(tmpdir).joinpath(os.path.join("tests", "__init__.py")),
        Path(tmpdir).joinpath(os.path.join("tests", "data", "__init__.py")),
    ]
    assert result == expected
