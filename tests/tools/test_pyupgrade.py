"""Check pyupgrade works."""

import difflib
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:

    from _pytest.capture import CaptureFixture


def test_pyupgrade(tmp_notebook_for_testing: Path, capsys: "CaptureFixture") -> None:
    """
    Check pyupgrade works. Should only reformat code cells.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`tmp_notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_for_testing) as handle:
        before = handle.readlines()
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")

    Path("pyproject.toml").write_text(
        dedent(
            """\
            [tool.nbqa.addopts]
            pyupgrade = ['--py36-plus']
            """
        )
    )
    main(["pyupgrade", os.path.abspath(path)])
    Path("pyproject.toml").unlink()
    with open(tmp_notebook_for_testing) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join(i for i in diff if any([i.startswith("+ "), i.startswith("- ")]))
    expected = dedent(
        """\
        -    \"    return 'hello {}'.format(name)\\n\",
        +    \"    return f'hello {name}'\\n\",
        """
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = f"Rewriting {path}\n"
    assert out == expected_out
    assert err == expected_err


def test_pyupgrade_works_with_empty_file(capsys: "CaptureFixture") -> None:
    """
    Check pyupgrade works with empty notebook.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", "footer.ipynb"))

    main(["pyupgrade", path])

    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_pyupgrade_works_with_weird_databricks_file(capsys: "CaptureFixture") -> None:
    """
    Check pyupgrade works with unusual databricks notebooks.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.join("tests", "data", "databricks_notebook.ipynb")
    main(["pyupgrade", path, "--nbqa-diff"])
    out, err = capsys.readouterr()
    expected_out = (
        f"\x1b[1mCell 2\x1b[0m\n------\n--- {path}\n"
        f"+++ {path}\n"
        "@@ -1 +1 @@\n"
        "\x1b[31m-set(())\n"
        "\x1b[0m\x1b[32m+set()\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    expected_err = f"Rewriting {path}\n"
    assert out == expected_out
    assert err == expected_err
