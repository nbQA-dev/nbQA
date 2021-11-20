"""
Extract markdown cells from notebook and save them to temporary markdown file.

Python cells, output, and metadata are ignored.
"""

import secrets
from collections import defaultdict
from typing import Any, DefaultDict, Mapping, MutableMapping, NamedTuple, Sequence

from nbqa.handle_magics import MagicHandler
from nbqa.notebook_info import NotebookInfo

MARKDOWN_SEPARATOR = f"# %%NBQA-MD-SEP{secrets.token_hex(3)}\n"


class Index(NamedTuple):
    """Keep track of line and cell number while iterating over cells."""

    line_number: int
    cell_number: int


def _parse_cell(
    source: Sequence[str],
) -> str:
    """
    Parse cell, replacing line magics with python code as placeholder.

    Parameters
    ----------
    source
        Source from notebook cell.

    Returns
    -------
    str
        Parsed cell.
    """
    parsed_cell = MARKDOWN_SEPARATOR
    parsed_cell += "".join(source)
    return f"{parsed_cell}\n"


def _get_line_numbers_for_mapping(
    cell_source: str,
) -> Mapping[int, int]:
    """Get the line number mapping from python file to notebook cell.

    Parameters
    ----------
    cell_source
        Source code of the notebook cell

    Returns
    -------
    Mapping[int, int]
        Line number mapping from temporary python file to notebook cell
    """
    lines_in_cell = cell_source.splitlines()
    line_mapping: MutableMapping[int, int] = {}

    line_mapping.update({i: i for i in range(len(lines_in_cell))})

    return line_mapping


def _should_ignore_markdown_cell(
    source: Sequence[str],
    skip_celltags: Sequence[str],
    tags: Sequence[str],
) -> bool:
    """
    Return True if the current cell should be ignored from processing.

    Parameters
    ----------
    source
        Source from the notebook cell

    Returns
    -------
    bool
        True if the cell should ignored else False
    """
    joined_source = "".join(source)
    if not joined_source or set(tags).intersection(skip_celltags):
        return True
    return False


def main(  # pylint: disable=R0914
    notebook_json: MutableMapping[str, Any],
    file_descriptor: int,
    skip_celltags: Sequence[str],
) -> NotebookInfo:
    """
    Extract code cells from notebook and save them in temporary Python file.

    Parameters
    ----------
    notebook_json
        Jupyter Notebook third-party tool is being run against.

    Returns
    -------
    NotebookInfo

    Raises
    ------
    AssertionError
        If hash collision (extremely rare event!)
    """
    cells = notebook_json["cells"]

    result = []
    cell_mapping = {0: "cell_0:0"}
    index = Index(line_number=0, cell_number=0)
    temporary_lines: DefaultDict[int, Sequence[MagicHandler]] = defaultdict(list)
    markdown_cells_to_ignore = set()

    whole_src = "".join(
        ["".join(cell["source"]) for cell in cells if cell["cell_type"] == "markdown"]
    )
    if MARKDOWN_SEPARATOR.strip() in whole_src:
        raise AssertionError(
            "Extremely rare hash collision occurred - please re-run nbQA to fix this"
        )

    for cell in cells:
        if cell["cell_type"] == "markdown":
            index = index._replace(cell_number=index.cell_number + 1)

            if _should_ignore_markdown_cell(
                cell["source"],
                skip_celltags,
                cell.get("metadata", {}).get("tags", []),
            ):
                markdown_cells_to_ignore.add(index.cell_number)
                continue

            parsed_cell = _parse_cell(cell["source"])

            cell_mapping.update(
                {
                    py_line
                    + index.line_number
                    + 1: f"cell_{index.cell_number}:{cell_line}"
                    for py_line, cell_line in _get_line_numbers_for_mapping(
                        parsed_cell,
                    ).items()
                }
            )
            result.append(parsed_cell)
            index = index._replace(
                line_number=index.line_number + len(parsed_cell.splitlines())
            )
            temporary_lines[index.cell_number] = []  # compatibility

    result_txt = "".join(result).rstrip("\n") + "\n" if result else ""
    with open(file_descriptor, "w", encoding="utf-8") as handle:
        handle.write(result_txt)

    return NotebookInfo(cell_mapping, set(), temporary_lines, markdown_cells_to_ignore)
