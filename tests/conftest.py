"""Define some fixtures that can be re-used between tests."""

import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pytest

if TYPE_CHECKING:
    from py._path.local import LocalPath


@pytest.fixture
def tmp_pyprojecttoml(tmpdir: "LocalPath") -> Iterator[Path]:
    """
    Temporarily delete pyproject.toml so it can be recreated during tests.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.
    """
    filename = Path("pyproject.toml")
    temp_file = Path(tmpdir) / filename
    shutil.copy(str(filename), str(temp_file))
    filename.unlink()
    yield filename
    shutil.copy(str(temp_file), str(filename))


@pytest.fixture(autouse=True)
def tmp_setupcfg(tmpdir: "LocalPath") -> Iterator[None]:
    """
    Temporarily delete setup.cfg so it can be recreated during tests.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.
    """
    filename = Path("setup.cfg")
    temp_file = Path(tmpdir) / filename
    shutil.copy(str(filename), str(temp_file))
    filename.unlink()
    yield
    shutil.copy(str(temp_file), str(filename))


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
    shutil.copy(str(filename), str(temp_file))
    yield filename
    shutil.copy(str(temp_file), str(filename))


@pytest.fixture
def tmp_unparseable(tmpdir: "LocalPath") -> Iterator[Path]:
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
    temp_file = Path(tmpdir) / "tmp.ipynb"
    temp_file.touch()
    temp_file.write_text("foo")
    yield temp_file


@pytest.fixture
def tmp_notebook_with_multiline(tmpdir: "LocalPath") -> Iterator[Path]:
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
    filename = Path("tests/data") / "clean_notebook_with_multiline.ipynb"
    temp_file = Path(tmpdir) / "tmp.ipynb"
    shutil.copy(str(filename), str(temp_file))
    yield filename
    shutil.copy(str(temp_file), str(filename))


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
    shutil.copy(str(filename), str(temp_file))
    yield filename
    shutil.copy(str(temp_file), str(filename))


@pytest.fixture
def tmp_notebook_with_trailing_semicolon(tmpdir: "LocalPath") -> Iterator[Path]:
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
    filename = Path("tests/data") / "notebook_with_trailing_semicolon.ipynb"
    temp_file = Path(tmpdir) / "tmp.ipynb"
    shutil.copy(str(filename), str(temp_file))
    yield filename
    shutil.copy(str(temp_file), str(filename))


@pytest.fixture
def tmp_remove_comments() -> Iterator[None]:
    """Make temporary copy of ``tests/remove_comments.py`` in root dir."""
    temp_file = Path("remove_comments.py")
    shutil.copy(str(Path("tests") / temp_file), str(temp_file))
    yield
    temp_file.unlink()
    del sys.modules["remove_comments"]
