"""Check project root is round correctly."""
from pathlib import Path
from typing import Iterable

import pytest

from nbqa.find_root import find_project_root


@pytest.mark.parametrize(
    "src",
    [
        (Path.cwd(),),
        (Path.cwd() / "tests", Path.cwd() / "tests/data"),
    ],
)
def test_find_project_root(src: Iterable[str]) -> None:
    """
    Check project root is found correctly.

    Parameters
    ----------
    src
        Source paths.
    """
    result = find_project_root(src)
    expected = Path.cwd()
    assert result == expected


def test_find_project_root_no_root_files() -> None:
    """Check root of filesystem is returned if no root file exists."""
    result = find_project_root((Path.cwd() / "tests",), (".this.does.not.exist",))
    expected = Path("/").resolve()
    assert result == expected
