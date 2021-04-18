"""Check :code:`isort` works as intended."""

import difflib
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import UnsupportedPackageVersionError, main

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
    main(["isort", path, "--nbqa-mutate"])

    with open(tmp_notebook_for_testing) as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        +    "import glob\\n",
        -    "\\n",
        -    "import glob\\n",
        """
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = f"Fixing {path}\n"
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
    main(["isort", path, "--nbqa-mutate"])

    with open(tmp_notebook_starting_with_md) as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        +    "import glob\\n",
        -    "\\n",
        -    "import glob\\n",
        """
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = f"Fixing {os.path.abspath(path)}\n"
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

    We will pass --treat-comment-as-code '# %%NBQA-CELL-SEP'.

    Parameters
    ----------
    notebook
        Notebook to run ``nbqa isort`` on.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.isort]
            addopts = --treat-comment-as-code "# %%%%NBQA-CELL-SEP"
            """
        )
    )

    path = os.path.abspath(os.path.join("tests", "data", notebook))
    main(["isort", path, "--nbqa-mutate"])

    Path("setup.cfg").unlink()

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
    main(["isort", path, "--nbqa-mutate"])

    with open(tmp_notebook_with_trailing_semicolon) as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        -    "import glob;\\n",
        +    "import glob\\n",
        -    "    pass;\\n",
        -    " "
        +    "    pass;"
        """
    )
    assert result == expected


def test_old_isort_separated_imports(capsys: "CaptureFixture") -> None:
    """
    Check isort works when a notebook has imports in different cells.

    This test would fail if we didn't pass --treat-comment-as-code '# %%NBQA-CELL-SEP'.
    """
    notebook = os.path.join(
        "tests", "data", "notebook_with_separated_imports_other.ipynb"
    )

    main(["isort", notebook, "--nbqa-diff"])
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    # check that adding extra command-line arguments doesn't interfere with
    # --treat-comment-as-code
    main(["isort", notebook, "--profile=black", "--nbqa-diff"])
    out, _ = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_old_isort(monkeypatch: "MonkeyPatch") -> None:
    """
    Check that using an old version of isort will raise an error.

    Parameters
    ----------
    monkeypatch
        Pytest fixture, we use it to override isort's version.
    """
    monkeypatch.setattr("nbqa.__main__.metadata.version", lambda _: "4.3.21")
    with pytest.raises(UnsupportedPackageVersionError) as excinfo:
        main(["isort", "tests/data/notebook_for_testing.ipynb"])

    msg = "\x1b[1mnbqa only works with isort >= 5.3.0, while you have 4.3.21 installed.\x1b[0m"
    assert msg == str(excinfo.value)
