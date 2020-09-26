"""Check that :code:`black` works as intended."""

import difflib
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:

    from _pytest.capture import CaptureFixture


def test_black_works(
    tmp_notebook_for_testing: "Path", capsys: "CaptureFixture"
) -> None:
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

    with open("setup.cfg", "w") as handle:
        handle.write(
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
    expected = (
        '+    "\\n",\n'
        '+    "\\n",\n'
        "-    \"    return 'hello {}'.format(name)\\n\",\n"
        '+    "    return \\"hello {}\\".format(name)\\n",\n'
        '-    "hello(3)   "\n'
        '+    "hello(3)"\n'
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = os.linesep.join(
        [f"reformatted {path}", "All done!   ", "1 file reformatted."]
    )
    assert out == expected_out
    for i in (0, 2):  # haven't figured out how to test the emojis part
        assert err.splitlines()[i] == expected_err.splitlines()[i]


def test_black_works_with_trailing_semicolons(
    tmp_notebook_with_trailing_semicolon: "Path", capsys: "CaptureFixture"
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

    with open("setup.cfg", "w") as handle:
        handle.write(
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
    expected = (
        '-    "import glob;\\n",\n'
        '+    "import glob\\n",\n'
        '-    "def func(a, b):\\n",\n'
        '+    "def func(\\n",\n'
        '+    "    a, b\\n",\n'
        '+    "):\\n",\n'
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = ""
    expected_err = os.linesep.join(
        [f"reformatted {path}", "All done!   ", "1 file reformatted."]
    )
    assert out == expected_out
    for i in (0, 2):  # haven't figured out how to test the emojis part
        assert err.splitlines()[i] == expected_err.splitlines()[i]
