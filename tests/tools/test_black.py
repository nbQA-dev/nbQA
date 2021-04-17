"""Check that :code:`black` works as intended."""

import difflib
import operator
import os
import subprocess
from pathlib import Path
from shutil import copyfile
from textwrap import dedent
from typing import TYPE_CHECKING, Callable

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from py._path.local import LocalPath

SPARKLES = "\N{sparkles}"
SHORTCAKE = "\N{shortcake}"
COLLISION = "\N{collision symbol}"
BROKEN_HEART = "\N{broken heart}"


def test_black_works(tmp_notebook_for_testing: Path, capsys: "CaptureFixture") -> None:
    """
    Check black works. Should only reformat code cells.

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
            black=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["black", path])
    Path("setup.cfg").unlink()
    with open(tmp_notebook_for_testing) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        -    \"    return 'hello {}'.format(name)\\n\",
        +    "    return \\"hello {}\\".format(name)\\n",
        -    "hello(3)   "
        +    "hello(3)"
        -    "    %time randint(5,10)"
        +    "    %time randint(5, 10)"
        """
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    # replace \u with \\u for both expected_err and err
    expected_err = (
        dedent(
            f"""\
            reformatted {path}
            All done! {SPARKLES} {SHORTCAKE} {SPARKLES}
            1 file reformatted.
            """
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    # This is required because linux supports emojis
    # so both should have \\ for comparison
    err = err.encode("ascii", "backslashreplace").decode()
    assert out == expected_out
    assert expected_err == err


def test_black_works_with_trailing_semicolons(
    tmp_notebook_with_trailing_semicolon: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check black works. Should only reformat code cells.

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
            black=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["black", path, "--line-length=10"])
    Path("setup.cfg").unlink()
    with open(tmp_notebook_with_trailing_semicolon) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        -    "import glob;\\n",
        +    "import glob\\n",
        -    "def func(a, b):\\n",
        -    "    pass;\\n",
        -    " "
        +    "def func(\\n",
        +    "    a, b\\n",
        +    "):\\n",
        +    "    pass;"
        """
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    # replace \u with \\u for both expected_err and err
    expected_err = (
        dedent(
            f"""\
            reformatted {path}
            All done! {SPARKLES} {SHORTCAKE} {SPARKLES}
            1 file reformatted.
            """
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    # This is required because linux supports emojis
    # so both should have \\ for comparison
    err = err.encode("ascii", "backslashreplace").decode()
    assert out == expected_out
    assert expected_err == err


def test_black_works_with_multiline(
    tmp_notebook_with_multiline: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check black works. Should only reformat code cells.

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
            black=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["black", path])
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
    # replace \u with \\u for both expected_err and err
    expected_err = (
        dedent(
            f"""\
            reformatted {path}
            All done! {SPARKLES} {SHORTCAKE} {SPARKLES}
            1 file reformatted.
            """
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    # This is required because linux supports emojis
    # so both should have \\ for comparison
    err = err.encode("ascii", "backslashreplace").decode()
    assert out == expected_out
    assert expected_err == err


def test_black_multiple_files(tmp_test_data: Path) -> None:
    """
    Check black works when running on a directory. Should reformat notebooks.

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
            black=1
            """
        )
    )
    with pytest.raises(SystemExit):
        main(["black", path])
    Path("setup.cfg").unlink()
    with open(str(tmp_test_data / "notebook_for_testing.ipynb")) as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    assert "".join(diff) != ""


def test_successive_runs_using_black(tmpdir: "LocalPath") -> None:
    """Check black returns 0 on the second run given a dirty notebook."""
    src_notebook = Path(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    test_notebook = Path(tmpdir) / src_notebook.name
    copyfile(src_notebook, test_notebook)

    def run_black(
        test_notebook: str, mod_time_compare_op: Callable[[float, float], bool]
    ) -> bool:
        """Run black using nbqa and validate the output."""
        mod_time_before: float = os.path.getmtime(test_notebook)
        output = subprocess.run(["nbqa", "black", test_notebook, "--nbqa-mutate"])
        mod_time_after: float = os.path.getmtime(test_notebook)
        return output.returncode == 0 and mod_time_compare_op(
            mod_time_after, mod_time_before
        )

    assert run_black(str(test_notebook), operator.gt)
    assert run_black(str(test_notebook), operator.eq)


def test_black_works_with_commented_magics(capsys: "CaptureFixture") -> None:
    """
    Check black works with notebooks with commented-out magics.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", "commented_out_magic.ipynb"))

    with pytest.raises(SystemExit):
        main(["black", path, "--nbqa-diff"])

    out, err = capsys.readouterr()
    err = err.encode("ascii", "backslashreplace").decode()
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
    expected_err = (
        dedent(
            f"""\
            reformatted {path}
            All done! {SPARKLES} {SHORTCAKE} {SPARKLES}
            1 file reformatted.
            """
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    assert expected_out == out
    assert expected_err == err


def test_black_works_with_leading_comment(capsys: "CaptureFixture") -> None:
    """
    Check black works with notebooks with commented-out magics.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", "starting_with_comment.ipynb"))

    with pytest.raises(SystemExit):
        main(["black", path, "--nbqa-diff"])

    out, err = capsys.readouterr()
    err = err.encode("ascii", "backslashreplace").decode()
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
    expected_err = (
        dedent(
            f"""\
            reformatted {path}
            All done! {SPARKLES} {SHORTCAKE} {SPARKLES}
            1 file reformatted.
            """
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    assert expected_out == out
    assert expected_err == err


def test_black_works_with_literal_assignment(capsys: "CaptureFixture") -> None:
    """
    Check black works with notebooks with invalid syntax (e.g. assignment to literal).

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(
        os.path.join("tests", "invalid_data", "assignment_to_literal.ipynb")
    )

    with pytest.raises(SystemExit):
        main(["black", path])

    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = (
        (
            f"error: cannot format {path}: "
            "cannot use --safe with this file; failed to parse source file.  AST error message: "
            "can't assign to literal (<unknown>, cell_1:1)\nOh no! "
            f"{COLLISION} {BROKEN_HEART} {COLLISION}\n1 file failed to reformat.\n"
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    # This is required because linux supports emojis
    # so both should have \\ for comparison
    err = err.encode("ascii", "backslashreplace").decode()

    assert expected_out == out
    assert expected_err == err


def test_not_allowlisted_magic(capsys: "CaptureFixture") -> None:
    """
    Notebook contains magic which isn't in the default allowlist.
    """
    path = os.path.abspath(os.path.join("tests", "data", "non_default_magic.ipynb"))

    with pytest.raises(SystemExit):
        main(["black", path])

    _, err = capsys.readouterr()
    assert "1 file left unchanged" in err


def test_allowlisted_magic(capsys: "CaptureFixture") -> None:
    """
    Notebook contains magic which is in the default allowlist.
    """
    path = os.path.abspath(os.path.join("tests", "data", "default_magic.ipynb"))
    with pytest.raises(SystemExit):
        main(["black", path, "--nbqa-diff"])
    out, _ = capsys.readouterr()
    expected = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"--- {path}\n"
        f"+++ {path}\n@@ -1,3 +1,3 @@\n"
        " %%timeit\n"
        " \n"
        "\x1b[31m-a = 2 \n"
        "\x1b[0m\x1b[32m+a = 2\n"
        "\x1b[0m\n"
        "To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`\n"
    )
    assert out == expected


def test_process_cells_magic(capsys: "CaptureFixture") -> None:
    """
    Notebook contains non-allowlist magic, but it's in process_cells.
    """
    path = os.path.abspath(os.path.join("tests", "data", "non_default_magic.ipynb"))
    with pytest.raises(SystemExit):
        main(["black", path, "--nbqa-diff", "--nbqa-process-cells", "javascript"])

    out, _ = capsys.readouterr()
    expected = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"--- {path}\n"
        f"+++ {path}\n"
        "@@ -1,3 +1,3 @@\n"
        " %%javascript\n"
        " \n"
        "\x1b[31m-a = 2 \n"
        "\x1b[0m\x1b[32m+a = 2\n"
        "\x1b[0m\n"
        "To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`\n"
    )
    assert out == expected


def test_invalid_syntax_with_nbqa_diff(capsys: "CaptureFixture") -> None:
    """
    Check that using nbqa-diff when there's invalid syntax doesn't have empty output.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(
        os.path.join("tests", "invalid_data", "assignment_to_literal.ipynb")
    )

    with pytest.raises(SystemExit):
        main(["black", path, "--nbqa-diff"])

    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = (
        (
            f"error: cannot format {path}: "
            "cannot use --safe with this file; failed to parse source file.  AST error message: "
            "can't assign to literal (<unknown>, cell_1:1)\nOh no! "
            f"{COLLISION} {BROKEN_HEART} {COLLISION}\n1 file failed to reformat.\n"
        )
        .encode("ascii", "backslashreplace")
        .decode()
    )
    # This is required because linux supports emojis
    # so both should have \\ for comparison
    err = err.encode("ascii", "backslashreplace").decode()

    assert expected_out == out
    assert expected_err == err


def test_comment_after_trailing_comma(capsys: "CaptureFixture") -> None:
    """
    Check trailing semicolon is still preserved if comment is after it.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(
        os.path.join("tests", "data", "comment_after_trailing_semicolon.ipynb")
    )

    with pytest.raises(SystemExit):
        main(["black", path, "--nbqa-diff"])

    out, _ = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"--- {path}\n"
        f"+++ {path}\n"
        "@@ -1,4 +1,5 @@\n"
        "\x1b[31m-import glob;\n"
        "\x1b[0m\x1b[32m+import glob\n"
        "\x1b[0m \n"
        " import nbqa;\n"
        "\x1b[32m+\n"
        "\x1b[0m # this is a comment\n"
        "\n"
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"--- {path}\n"
        f"+++ {path}\n"
        "@@ -1,3 +1,2 @@\n"
        " def func(a, b):\n"
        "     pass;\n"
        "\x1b[31m- \n"
        "\x1b[0m\n"
        "To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`\n"
    )
    assert out == expected_out
