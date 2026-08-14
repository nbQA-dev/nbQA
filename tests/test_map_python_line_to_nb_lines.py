"""Check output from third-party tool is correctly parsed."""

import os
from textwrap import dedent
from typing import TYPE_CHECKING

from nbqa.__main__ import main
from nbqa.output_parser import map_python_line_to_nb_lines
from nbqa.save_code_source import _get_line_numbers_for_mapping

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_map_python_line_to_nb_lines() -> None:
    """Check that the output is correctly parsed if there is a warning about line 0."""
    out = "notebook.ipynb:0:1: WPS102 Found incorrect module name pattern"
    err = ""
    notebook = "notebook.ipynb"
    cell_mapping = {0: "cell_0:0"}
    result, _ = map_python_line_to_nb_lines("flake8", out, err, notebook, cell_mapping)
    expected = "notebook.ipynb:cell_0:0:1: WPS102 Found incorrect module name pattern"
    assert result == expected


def test_black_unparseable_output() -> None:
    """Check that the output is correctly parsed if ``black`` fails to reformat."""
    out = ""
    err = dedent("""\
        error: cannot format notebook.ipynb: Cannot parse: 38:5: invalid syntax
        Oh no! 💥 💔 💥
        1 file failed to reformat.
        """)
    notebook = "notebook.ipynb"
    cell_mapping = {38: "cell_10:1"}
    _, result = map_python_line_to_nb_lines("black", out, err, notebook, cell_mapping)
    expected = dedent("""\
        error: cannot format notebook.ipynb: Cannot parse: cell_10:1:5: invalid syntax
        Oh no! 💥 💔 💥
        1 file failed to reformat.
        """)
    assert result == expected


def test_separator_line_maps_to_first_line_of_cell() -> None:
    """The line nbQA inserts itself must not map to cell line 0."""
    parsed_cell = "# %%NBQA-CELL-SEPabc123\nimport math\nimport random\n"
    mapping = _get_line_numbers_for_mapping(parsed_cell, [])
    assert mapping == {0: 1, 1: 1, 2: 2}


def test_module_level_diagnostic_is_reported_at_line_one(
    capsys: "CaptureFixture",
) -> None:
    """A message about the whole module must point at the first line of cell 1."""
    notebook = os.path.join("tests", "data", "simple_imports.ipynb")
    main(["pylint", notebook, "--disable=all", "--enable=C0114"])
    out, _ = capsys.readouterr()
    assert "cell_1:0:" not in out
    assert f"{notebook}:cell_1:1:0: C0114" in out
