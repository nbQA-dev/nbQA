"""Check :code:`isort` works as intended."""

import difflib
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


def test_isort_works(tmp_notebook_for_testing: Path, capsys: "CaptureFixture") -> None:
    """
    Check isort works.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_for_testing) as handle:
        before = handle.readlines()
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    with pytest.raises(SystemExit):
        main(["isort", path, "--nbqa-mutate"])

    with open(tmp_notebook_for_testing) as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = '+    "import glob\\n",\n-    "\\n",\n-    "import glob\\n",\n'
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = f"Fixing {path}{os.linesep}"
    expected_err = ""
    assert out == expected_out
    assert err == expected_err


def test_isort_initial_md(
    tmp_notebook_starting_with_md: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check isort works when a notebook starts with a markdown cell.

    Parameters
    ----------
    tmp_notebook_starting_with_md
        Temporary copy of :code:`notebook_starting_with_md.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_starting_with_md) as handle:
        before = handle.readlines()
    path = os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
    with pytest.raises(SystemExit):
        main(["isort", path, "--nbqa-mutate"])

    with open(tmp_notebook_starting_with_md) as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = '+    "import glob\\n",\n-    "\\n",\n-    "import glob\\n",\n'
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = f"Fixing {path}{os.linesep}"
    expected_err = ""
    assert out == expected_out
    assert err == expected_err


@pytest.mark.parametrize(
    "notebook",
    [
        "notebook_with_separated_imports.ipynb",
        "notebook_with_separated_imports_other.ipynb",
    ],
)
def test_isort_separated_imports(notebook: str, capsys: "CaptureFixture") -> None:
    """
    Check isort works when a notebook has imports in different cells.

    Parameters
    ----------
    notebook
        Notebook to run ``nbqa isort`` on.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", notebook))
    with pytest.raises(SystemExit):
        main(["isort", path])

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = ""
    assert out == expected_out
    assert err == expected_err


def test_isort_trailing_semicolon(tmp_notebook_with_trailing_semicolon: Path) -> None:
    """
    Check isort works when a notebook starts with a markdown cell.

    Parameters
    ----------
    tmp_notebook_with_trailing_semicolon
        Temporary copy of :code:`notebook_with_trailing_semicolon.ipynb`.
    """
    # check diff
    with open(tmp_notebook_with_trailing_semicolon) as handle:
        before = handle.readlines()
    path = os.path.abspath(
        os.path.join("tests", "data", "notebook_with_trailing_semicolon.ipynb")
    )
    with pytest.raises(SystemExit):
        main(["isort", path, "--nbqa-mutate"])

    with open(tmp_notebook_with_trailing_semicolon) as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = (
        '-    "import glob;\\n",\n'
        '+    "import glob\\n",\n'
        '-    "    pass;\\n",\n'
        '-    " "\n'
        '+    "    pass;"\n'
    )
    assert result == expected


def test_old_isort_separated_imports(
    tmp_test_data: Path, capsys: "CaptureFixture", monkeypatch: "MonkeyPatch"
) -> None:
    """
    Check isort works when a notebook has imports in different cells.

    We will not pass --treat-comment-as-code '# %%' in old version of isort.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    capsys
        Pytest fixture to capture stdout and stderr.
    monkeypatch
        Pytest fixture, we use it to override isort's version.
    """
    notebook = tmp_test_data / "notebook_with_separated_imports_other.ipynb"

    with open(notebook) as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["isort", str(notebook), "--nbqa-mutate"])
    with open(notebook) as handle:
        after = handle.readlines()
    assert before == after

    monkeypatch.setattr("nbqa.config.ISORT_MODULE.__version__", "4.3.21")
    with open(notebook) as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["isort", str(notebook), "--nbqa-mutate"])
    with open(notebook) as handle:
        after = handle.readlines()
    assert before != after

    # Check nbqa still works if there is no isort installed.
    monkeypatch.setattr("nbqa.config.ISORT_MODULE", None)
    with pytest.raises(SystemExit):
        main(["black", str(notebook)])
    _, err = capsys.readouterr()
    assert "1 file left unchanged" in err
