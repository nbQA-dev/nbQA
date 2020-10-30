"""Check output from third-party tool is correctly parsed."""

from pathlib import Path

from nbqa.__main__ import _map_python_line_to_nb_lines


def test_map_python_line_to_nb_lines() -> None:
    """Check that the output is correctly parsed if there is a warning about line 0."""
    out = "notebook.ipynb:0:1: WPS102 Found incorrect module name pattern"
    notebook = Path("notebook.ipynb")
    cell_mapping = {0: "cell_0:0"}
    result = _map_python_line_to_nb_lines(out, notebook, cell_mapping)
    expected = "notebook.ipynb:cell_0:0:1: WPS102 Found incorrect module name pattern"
    assert result == expected
