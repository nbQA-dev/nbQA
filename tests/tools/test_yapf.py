"""Check that :code:`yapf` works as intended."""

import difflib
import operator
import os
import subprocess
from pathlib import Path
from shutil import copyfile
from textwrap import dedent
from typing import TYPE_CHECKING, Callable, List

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from py._path.local import LocalPath

SPARKLES = "\N{sparkles}"
SHORTCAKE = "\N{shortcake}"
COLLISION = "\N{collision symbol}"
BROKEN_HEART = "\N{broken heart}"


def test_yapf_works(tmp_notebook_for_testing: Path, capsys: "CaptureFixture") -> None:
    """
    Check yapf works. Should only reformat code cells.

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

    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.mutate]
            yapf=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["yapf", "--in-place", path])
    Path("setup.cfg").unlink()
    with open(tmp_notebook_for_testing) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        -    "hello(3)   "
        +    "hello(3)"
        -    "    %time randint(5,10)"
        +    "    %time randint(5, 10)"
        -    "    %time pretty_print_object = pprint.PrettyPrinter(\\\\\\n",
        -    "              indent=4, width=80, stream=sys.stdout, compact=True, depth=5\\\\\\n",
        -    "          )\\n",
        +    "    %time pretty_print_object = pprint.PrettyPrinter(indent=4,\\\\\\n",
        +    "                                                     width=80,\\\\\\n",
        +    "                                                     stream=sys.stdout,\\\\\\n",
        +    "                                                     compact=True,\\\\\\n",
        +    "                                                     depth=5)\\n",
        """
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = ""
    assert out == expected_out
    assert err == expected_err


def test_yapf_works_with_trailing_semicolons(
    tmp_notebook_with_trailing_semicolon: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check yapf works. Should only reformat code cells.

    Parameters
    ----------
    tmp_notebook_with_trailing_semicolon
        Temporary copy of :code:`notebook_with_trailing_semicolon.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_with_trailing_semicolon) as handle:
        before = handle.readlines()
    path = os.path.abspath(
        os.path.join("tests", "data", "notebook_with_trailing_semicolon.ipynb")
    )

    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.mutate]
            yapf=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["yapf", "--in-place", path])
    Path("setup.cfg").unlink()
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

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = ""
    assert out == expected_out
    assert err == expected_err


def test_yapf_works_with_multiline(
    tmp_notebook_with_multiline: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check yapf works. Should only reformat code cells.

    Parameters
    ----------
    tmp_notebook_with_multiline
        Temporary copy of :code:`clean_notebook_with_multiline.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check diff
    with open(tmp_notebook_with_multiline) as handle:
        before = handle.readlines()
    path = os.path.abspath(
        os.path.join("tests", "data", "clean_notebook_with_multiline.ipynb")
    )

    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.mutate]
            yapf=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["yapf", "--in-place", path])
    Path("setup.cfg").unlink()
    with open(tmp_notebook_with_multiline) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        -    "assert 1 + 1 == 2;  assert 1 + 1 == 2;"
        +    "assert 1 + 1 == 2\\n",
        +    "assert 1 + 1 == 2;"
        """
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = ""
    assert out == expected_out
    assert err == expected_err


def test_yapf_multiple_files(tmp_test_data: Path) -> None:
    """
    Check yapf works when running on a directory. Should reformat notebooks.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    # check diff
    with open(str(tmp_test_data / "notebook_for_testing.ipynb")) as handle:
        before = handle.readlines()
    path = os.path.abspath(os.path.join("tests", "data"))

    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.mutate]
            yapf=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["yapf", "--in-place", "--recursive", path])
    Path("setup.cfg").unlink()
    with open(str(tmp_test_data / "notebook_for_testing.ipynb")) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    assert "".join(diff) != ""


def test_successive_runs_using_yapf(tmpdir: "LocalPath") -> None:
    """Check yapf returns 0 on the second run given a dirty notebook."""
    src_notebook = Path(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    test_notebook = Path(tmpdir) / src_notebook.name
    copyfile(src_notebook, test_notebook)

    def run_yapf(
        test_notebook: str, content_compare_op: Callable[[List[str], List[str]], bool]
    ) -> bool:
        """Run yapf using nbqa and validate the output."""
        with open(test_notebook) as test_file:
            before_contents: List[str] = test_file.readlines()
        output = subprocess.run(
            ["nbqa", "yapf", "--in-place", test_notebook, "--nbqa-mutate"]
        )
        with open(test_notebook) as test_file:
            after_contents: List[str] = test_file.readlines()
        return output.returncode == 0 and content_compare_op(
            before_contents, after_contents
        )

    assert run_yapf(str(test_notebook), operator.ne)
    assert run_yapf(str(test_notebook), operator.eq)


def test_yapf_works_with_commented_magics(capsys: "CaptureFixture") -> None:
    """
    Check yapf works with notebooks with commented-out magics.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", "commented_out_magic.ipynb"))

    with pytest.raises(SystemExit):
        main(["yapf", "--in-place", path, "--nbqa-diff"])

    out, err = capsys.readouterr()
    expected_out = f"""\
\x1b[1mCell 1\x1b[0m
------
--- {path}
+++ {path}
@@ -1,2 +1 @@
\x1b[31m-[1, 2,
\x1b[0m\x1b[31m-3, 4]
\x1b[0m\x1b[32m+[1, 2, 3, 4]
\x1b[0m
To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`
"""
    expected_err = ""
    assert expected_out == out
    assert expected_err == err


def test_yapf_works_with_leading_comment(capsys: "CaptureFixture") -> None:
    """
    Check yapf works with notebooks with commented-out magics.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", "starting_with_comment.ipynb"))

    with pytest.raises(SystemExit):
        main(["yapf", "--in-place", path, "--nbqa-diff"])

    out, err = capsys.readouterr()
    expected_out = f"""\
\x1b[1mCell 3\x1b[0m
------
--- {path}
+++ {path}
@@ -1,3 +1,3 @@
 # export
\x1b[31m-def example_func(hi = "yo"):
\x1b[0m\x1b[32m+def example_func(hi="yo"):
\x1b[0m     pass

To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`
"""
    expected_err = ""
    assert expected_out == out
    assert expected_err == err
