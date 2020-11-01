"""Check output from third-party tool is correctly parsed."""

from pathlib import Path
from textwrap import dedent

from nbqa.__main__ import _map_python_line_to_nb_lines


def test_map_python_line_to_nb_lines() -> None:
    """Check that the output is correctly parsed if there is a warning about line 0."""
    out = "notebook.ipynb:0:1: WPS102 Found incorrect module name pattern"
    err = ""
    notebook = Path("notebook.ipynb")
    cell_mapping = {0: "cell_0:0"}
    result, _ = _map_python_line_to_nb_lines(out, err, notebook, cell_mapping)
    expected = "notebook.ipynb:cell_0:0:1: WPS102 Found incorrect module name pattern"
    assert result == expected


def test_black_unparseable_output() -> None:
    """Check that the output is correctly parsed if there is a warning about line 0."""
    out = ""
    err = dedent(
        """\
        error: cannot format notebook.ipynb: Cannot parse: 38:5: invalid syntax
        Oh no! 💥 💔 💥
        1 file failed to reformat.
        """
    )
    notebook = Path("notebook.ipynb")
    cell_mapping = {38: "cell_10:1"}
    _, result = _map_python_line_to_nb_lines(out, err, notebook, cell_mapping)
    expected = dedent(
        """\
        error: cannot format notebook.ipynb: Cannot parse: cell_10:1:5: invalid syntax
        Oh no! 💥 💔 💥
        1 file failed to reformat.
        """
    )
    assert result == expected
