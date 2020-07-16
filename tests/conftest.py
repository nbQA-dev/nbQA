import shutil
from pathlib import Path

import pytest


@pytest.fixture
def tmp_notebook_for_testing(tmpdir):
    """
    Make temporary copy of test notebook before it's operated on, then revert it.
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
def tmp_notebook_starting_with_md(tmpdir):
    """
    Make temporary copy of test notebook before it's operated on, then revert it.
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
