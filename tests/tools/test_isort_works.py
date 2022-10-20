"""Check :code:`isort` works as intended."""
import difflib
import json
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
    with open(tmp_notebook_for_testing, encoding="utf-8") as handle:
        before = handle.readlines()
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    main(["isort", path])

    with open(tmp_notebook_for_testing, encoding="utf-8") as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join(i for i in diff if any([i.startswith("+ "), i.startswith("- ")]))

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
    with open(tmp_notebook_starting_with_md, encoding="utf-8") as handle:
        before = handle.readlines()
    path = os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
    main(["isort", path])

    with open(tmp_notebook_starting_with_md, encoding="utf-8") as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join(i for i in diff if any([i.startswith("+ "), i.startswith("- ")]))

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
    Path("pyproject.toml").write_text(
        dedent(
            """\
            [tool.nbqa.isort]
            addopts = ["--treat-comment-as-code=# %%NBQA-CELL-SEP"]
            """
        ),
        encoding="utf-8",
    )

    path = os.path.abspath(os.path.join("tests", "data", notebook))
    main(["isort", path])
    Path("pyproject.toml").unlink()

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
    with open(tmp_notebook_with_trailing_semicolon, encoding="utf-8") as handle:
        before = handle.readlines()
    path = os.path.abspath(
        os.path.join("tests", "data", "notebook_with_trailing_semicolon.ipynb")
    )
    main(["isort", path])

    with open(tmp_notebook_with_trailing_semicolon, encoding="utf-8") as handle:
        after = handle.readlines()
    diff = difflib.unified_diff(before, after)
    result = "".join(i for i in diff if any([i.startswith("+ "), i.startswith("- ")]))

    expected = '-    "import glob;\\n",\n+    "import glob\\n",\n'
    assert result == expected


def test_old_isort_separated_imports(tmp_test_data: Path) -> None:
    """
    Check isort works when a notebook has imports in different cells.

    This test would fail if we didn't pass --treat-comment-as-code '# %%NBQA-CELL-SEP'.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    notebook = tmp_test_data / "notebook_with_separated_imports_other.ipynb"

    before_mtime = os.path.getmtime(str(notebook))
    main(["isort", str(notebook)])
    assert os.path.getmtime(str(notebook)) == before_mtime

    # check that adding extra command-line arguments doesn't interfere with
    # --treat-comment-as-code
    main(["isort", str(notebook), "--profile=black"])
    assert os.path.getmtime(str(notebook)) == before_mtime


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


def test_comment_after_trailing_semicolons(capsys: "CaptureFixture") -> None:
    """Check isort works normally when there's a comment after trailing semicolon."""
    # check diff
    path = os.path.abspath(
        os.path.join("tests", "data", "comment_after_trailing_semicolon.ipynb")
    )

    main(["isort", path, "--nbqa-diff"])

    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1,4 +1,5 @@\n"
        "\x1b[0m\x1b[31m-import glob;\n"
        "\x1b[0m\x1b[32m+import glob\n"
        "\x1b[0m\x1b[32m+\n"
        "\x1b[0m\n"
        f"Fixing {path}\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected_out


def test_return_code_false_positive() -> None:
    """
    Check return code is 0 when running with ``--lines-after-imports=2``.
    """
    notebook = os.path.join(
        "tests", "data", "notebook_with_separated_imports_other.ipynb"
    )

    result = main(["isort", str(notebook), "--nbqa-diff", "--lines-after-imports=2"])
    assert result == 0

    result = main(["isort", str(notebook), "--nbqa-diff", "--float-to-top"])
    assert result == 1


def test_float_to_top(tmp_test_data: Path) -> None:
    """
    Check isort works when a notebook has imports in different cells.

    This test would fail if we didn't pass --treat-comment-as-code '# %%NBQA-CELL-SEP'.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    notebook = tmp_test_data / "notebook_with_separated_imports_other.ipynb"

    main(["isort", str(notebook), "--float-to-top"])

    with open(notebook, encoding="utf-8") as fd:
        result = json.load(fd)["cells"]
    expected = [
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "\n",
                "# This is a comment on the second import\n",
                "import numpy",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [],
        },
    ]
    assert result == expected


def test_float_to_top_starting_markdown(tmp_test_data: Path) -> None:
    """
    Check isort works when a notebook has markdown in first cell.

    The --float-to-top option would previously have removed the wrong cell.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    notebook = tmp_test_data / "markdown_then_imports.ipynb"

    main(["isort", str(notebook), "--float-to-top"])

    with open(notebook, encoding="utf-8") as fd:
        result = json.load(fd)["cells"]
    expected = [
        {"cell_type": "markdown", "metadata": {}, "source": ["hello world"]},
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["import os\n", "import sys"],
        },
    ]
    assert result == expected
