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
from typing import (
    TYPE_CHECKING,
    Any,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Sequence,
    Set,
)

import tokenize_rt

from nbqa.handle_magics import MagicHandler
from nbqa.notebook_info import NotebookInfo
from nbqa.save_source import CODE_SEPARATOR
from nbqa.text import BOLD, GREEN, RED, RESET

if TYPE_CHECKING:
    from pathlib import Path


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

    Raises
    ------
    AssertionError
        If code thought to be unreachable is reached.
    """
    if cell_number in trailing_semicolons:
        tokens = tokenize_rt.src_to_tokens(source)
        for idx, token in tokenize_rt.reversed_enumerate(tokens):
            if not token.src.strip(" \n") or token.name == "COMMENT":
                continue
            tokens[idx] = token._replace(src=token.src + ";")
            break
        else:  # pragma: nocover
            raise AssertionError(
                "Unreachable code, please report bug at https://github.com/nbQA-dev/nbQA/issues"
            )
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
        source = magic_substitution.restore_magic(source)
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


def _get_pycells(python_file: str) -> Iterator[str]:
    """
    Parse cells from Python file.

    Parameters
    ----------
    python_file
        Temporary Python file notebook was converted to.

    Returns
    -------
    Iterator
        Parsed cells.
    """
    with open(python_file, encoding="utf-8") as handle:
        txt = handle.read()
    if txt.startswith(CODE_SEPARATOR):
        txt = txt[len(CODE_SEPARATOR) :]
    return iter(txt.split(CODE_SEPARATOR))


def _notebook_code_cells(
    notebook_json: Mapping[str, Any]
) -> Iterator[MutableMapping[str, Any]]:
    """
    Iterate through notebook's code cells.

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
        if cell["cell_type"] == "code":
            yield cell


def mutate(python_file: str, notebook: "Path", notebook_info: NotebookInfo) -> bool:
    """
    Replace :code:`source` code cells of original notebook.

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
        Whether mutation actually happened.
    """
    notebook_json = json.loads(notebook.read_text(encoding="utf-8"))
    original_notebook_json = copy.deepcopy(notebook_json)

    pycells = _get_pycells(python_file)
    for code_cell_number, cell in enumerate(
        _notebook_code_cells(notebook_json), start=1
    ):
        if code_cell_number in notebook_info.code_cells_to_ignore:
            continue
        cell["source"] = _get_new_source(code_cell_number, notebook_info, next(pycells))

    if original_notebook_json == notebook_json:
        return False

    temp_notebook = os.path.join(os.path.dirname(python_file), notebook.name)
    with open(temp_notebook, "w", encoding="utf-8") as handle:
        handle.write(f"{json.dumps(notebook_json, indent=1, ensure_ascii=False)}\n")
    move(str(temp_notebook), str(notebook))
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
    line_changes = []
    for line in cell_diff:
        if line.startswith("+++") or line.startswith("---"):
            line_changes.append(line)
        elif line.startswith("+"):
            line_changes.append(f"{GREEN}{line}{RESET}")
        elif line.startswith("-"):
            line_changes.append(f"{RED}{line}{RESET}")
        else:
            line_changes.append(line)

    if line_changes:
        header = f"Cell {code_cell_number}"
        headers = [f"{BOLD}{header}{RESET}\n", f"{'-'*len(header)}\n"]
        sys.stdout.writelines(headers + line_changes + ["\n"])
        return True
    return False


def diff(python_file: str, notebook: "Path", notebook_info: NotebookInfo) -> bool:
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
    notebook_json = json.loads(notebook.read_text(encoding="utf-8"))

    pycells = _get_pycells(python_file)

    actually_mutated = False

    for code_cell_number, cell in enumerate(
        _notebook_code_cells(notebook_json), start=1
    ):
        if code_cell_number in notebook_info.code_cells_to_ignore:
            continue
        new_source = _get_new_source(code_cell_number, notebook_info, next(pycells))
        cell["source"][-1] += "\n"
        new_source[-1] += "\n"
        cell_diff = unified_diff(
            cell["source"],
            new_source,
            fromfile=str(notebook),
            tofile=str(notebook),
        )
        actually_mutated = _print_diff(code_cell_number, cell_diff) or actually_mutated
    return actually_mutated
