"""
Replace :code:`source` code cells of original notebook with ones from converted file.

The converted file will have had the third-party tool run against it by now.
"""

import copy
import json
import os
import sys
from difflib import unified_diff
from shutil import move
from typing import Any, Iterator, List, Mapping, MutableMapping, Sequence, Set

import tokenize_rt

from nbqa.handle_magics import MagicHandler
from nbqa.notebook_info import NotebookInfo
from nbqa.save_code_source import CODE_SEPARATOR
from nbqa.save_markdown_source import MARKDOWN_SEPARATOR
from nbqa.text import BOLD, RESET

SOURCE = {True: "markdown", False: "code"}
SEPARATOR = {True: MARKDOWN_SEPARATOR, False: CODE_SEPARATOR}


def _restore_semicolon(
    source: str,
    cell_number: int,
    trailing_semicolons: Set[int],
) -> str:
    """
    Restore the semicolon at the end of the cell.

    Restore the trailing semicolon if the cell originally contained semicolon
    and the third party tool removed it.

    Parameters
    ----------
    source
        Portion of Python file between cell separators.
    cell_number
        Number of current cell.
    trailing_semicolons
        List of cells which originally had trailing semicolons.

    Returns
    -------
    str
        New source with removed semicolon restored.
    """
    if cell_number in trailing_semicolons:
        tokens = tokenize_rt.src_to_tokens(source)
        for idx, token in tokenize_rt.reversed_enumerate(tokens):
            if not token.src.strip(" \n") or token.name == "COMMENT":
                continue
            tokens[idx] = token._replace(src=token.src + ";")
            break
        source = tokenize_rt.tokens_to_src(tokens)
    return source


def _reinstate_magics(
    source: str,
    temporary_lines: Sequence[MagicHandler],
) -> List[str]:
    """
    Put (preprocessed) line magics back in.

    Parameters
    ----------
    source
        Portion of Python file between cell separators.
    temporary_lines
        Mapping from temporary magic substitutions to original ipython magics

    Returns
    -------
    List[str]
        New source that can be saved into Jupyter Notebook.
    """
    for magic_substitution in temporary_lines:
        source = source.replace(magic_substitution.replacement, magic_substitution.src)
    return source.strip("\n").splitlines(True)


def _get_new_source(
    code_cell_number: int,
    notebook_info: NotebookInfo,
    pycell: str,
) -> List[str]:
    """
    Get new source to replace original one with.

    Parameters
    ----------
    code_cell_number
        Cell number (we start counting from 1).
    notebook_info
        Information about notebook cells used for processing
    pycell
        Cell from temporary Python script.

    Returns
    -------
    List
        New source for cell.
    """
    source = _restore_semicolon(
        pycell, code_cell_number, notebook_info.trailing_semicolons
    )
    return _reinstate_magics(
        source,
        notebook_info.temporary_lines.get(code_cell_number, []),
    )


def _get_cells(tmp_file: str, num_cells: int, *, md: bool) -> Iterator[str]:
    """
    Parse cells from Python file.

    Parameters
    ----------
    tmp_file
        Temporary file notebook was converted to.

    Returns
    -------
    Iterator
        Parsed cells.

    Raises
    ------
    ValueError
        If the third-party tool "ate" any separator comments.
    """
    with open(tmp_file, encoding="utf-8") as handle:
        txt = handle.read()
    separator = SEPARATOR[md]

    if txt.count(separator) != num_cells:
        raise ValueError(
            "Tool did not preserve code separators and cannot be safely used with nbQA."
        )

    if txt.startswith(separator):
        txt = txt[len(separator) :]
    return iter(txt.split(separator))


def _notebook_cells(
    notebook_json: Mapping[str, Any],
    *,
    md: bool,
) -> Iterator[MutableMapping[str, Any]]:
    """
    Iterate through notebook's cells.

    Parameters
    ----------
    notebook_json
        json-parsed notebook.

    Yields
    ------
    MutableMapping[str, Any]
        Cell content.
    """
    for cell in notebook_json["cells"]:
        if cell["cell_type"] == SOURCE[md]:
            yield cell


def mutate(
    temp_file: str, notebook: str, notebook_info: NotebookInfo, *, md: bool
) -> bool:
    """
    Replace :code:`source` code cells of original notebook.

    Parameters
    ----------
    temp_file
        Temporary Python file notebook was converted to.
    notebook
        Jupyter Notebook third-party tool is run against (unmodified).
    notebook_info
        Information about notebook cells used for processing

    Returns
    -------
    bool
        Whether mutation actually happened.
    """
    with open(notebook, encoding="utf-8") as handle:
        notebook_txt = handle.read()
    notebook_json = json.loads(notebook_txt)
    original_notebook_json = copy.deepcopy(notebook_json)

    cells = _get_cells(temp_file, len(notebook_info.temporary_lines), md=md)
    for code_cell_number, cell in enumerate(
        _notebook_cells(notebook_json, md=md), start=1
    ):
        if code_cell_number in notebook_info.code_cells_to_ignore:
            continue
        cell["source"] = _get_new_source(code_cell_number, notebook_info, next(cells))

    if original_notebook_json == notebook_json:
        return False

    temp_notebook = os.path.join(os.path.dirname(temp_file), os.path.basename(notebook))
    with open(temp_notebook, "w", encoding="utf-8") as handle:
        if notebook_txt.endswith("\n"):
            handle.write(f"{json.dumps(notebook_json, indent=1, ensure_ascii=False)}\n")
        else:
            handle.write(f"{json.dumps(notebook_json, indent=1, ensure_ascii=False)}")
    move(temp_notebook, notebook)
    return True


def _print_diff(code_cell_number: int, cell_diff: Iterator[str]) -> bool:
    """
    Print diff between cells, colouring as appropriate.

    Parameters
    ----------
    code_cell_number
        Current cell number
    cell_diff
        Diff between original and new versions of cell.

    Returns
    -------
    bool
        Whether non-null diff was printed.
    """
    # https://github.com/psf/black/blob/9a73bb86db59de1e12426fec81dcdb7f3bb9be7b/src/black/output.py#L79-L92
    line_changes = []
    for line in cell_diff:

        if line.startswith("+++") or line.startswith("---"):
            line_changes.append("\033[1;37m" + line + "\033[0m")  # bold white, reset
        elif line.startswith("@@"):
            line_changes.append("\033[36m" + line + "\033[0m")  # cyan, reset
        elif line.startswith("+"):
            line_changes.append("\033[32m" + line + "\033[0m")  # green, reset
        elif line.startswith("-"):
            line_changes.append("\033[31m" + line + "\033[0m")  # red, reset

    if line_changes:
        header = f"Cell {code_cell_number}"
        headers = [f"{BOLD}{header}{RESET}\n", f"{'-'*len(header)}\n"]
        sys.stdout.writelines(headers + line_changes + ["\n"])
        return True
    return False


def diff(
    python_file: str, notebook: str, notebook_info: NotebookInfo, *, md: bool
) -> bool:
    """
    View diff between new source of code cells and original sources.

    Parameters
    ----------
    python_file
        Temporary Python file notebook was converted to.
    notebook
        Jupyter Notebook third-party tool is run against (unmodified).
    notebook_info
        Information about notebook cells used for processing

    Returns
    -------
    bool
        Whether non-null diff was produced.
    """
    with open(notebook, encoding="utf-8") as handle:
        notebook_json = json.loads(handle.read())

    cells = _get_cells(python_file, len(notebook_info.temporary_lines), md=md)

    actually_mutated = False

    for code_cell_number, cell in enumerate(
        _notebook_cells(notebook_json, md=md), start=1
    ):
        if code_cell_number in notebook_info.code_cells_to_ignore:
            continue
        new_source = _get_new_source(code_cell_number, notebook_info, next(cells))
        cell["source"][-1] += "\n"
        if new_source:
            new_source[-1] += "\n"
        else:
            new_source = ["\n"]
        cell_diff = unified_diff(
            cell["source"],
            new_source,
            fromfile=notebook,
            tofile=notebook,
        )
        actually_mutated = _print_diff(code_cell_number, cell_diff) or actually_mutated
    return actually_mutated
