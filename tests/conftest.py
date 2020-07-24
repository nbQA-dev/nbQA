"""
Define some fixtures that can be re-used between tests.
"""

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pytest

if TYPE_CHECKING:
    from py._path.local import LocalPath


@pytest.fixture
def tmp_notebook_for_testing(tmpdir: "LocalPath") -> Iterator[Path]:
    """
    Make temporary copy of test notebook before it's operated on, then revert it.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.

    Yields
    ------
    Path
        Temporary copy of test notebook.
    """
    filename = Path("tests/data") / "notebook_for_testing.ipynb"
    temp_file = Path(tmpdir) / "tmp.ipynb"
    shutil.copy(
        str(filename), str(temp_file),
    )
    yield filename
    shutil.copy(
        str(temp_file), str(filename),
    )


@pytest.fixture
def tmp_notebook_starting_with_md(tmpdir: "LocalPath") -> Iterator[Path]:
    """
    Make temporary copy of test notebook before it's operated on, then revert it.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.

    Yields
    ------
    Path
        Temporary copy of notebook.
    """
    filename = Path("tests/data") / "notebook_starting_with_md.ipynb"
    temp_file = Path(tmpdir) / "tmp.ipynb"
    shutil.copy(
        str(filename), str(temp_file),
    )
    yield filename
    shutil.copy(
        str(temp_file), str(filename),
    )
