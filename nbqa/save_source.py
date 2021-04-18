"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import ast
import json
import re
from collections import defaultdict
from itertools import takewhile
from textwrap import indent
from typing import (
    TYPE_CHECKING,
    DefaultDict,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    NamedTuple,
    Sequence,
    Tuple,
)

import tokenize_rt

from nbqa.handle_magics import INPUT_SPLITTER, IPythonMagicType, MagicHandler
from nbqa.notebook_info import NotebookInfo

if TYPE_CHECKING:
    from pathlib import Path

CODE_SEPARATOR = "# %%NBQA-CELL-SEP\n"
MAGIC = ["time", "timeit", "capture", "pypy", "python", "python3"]
NEWLINE = "\n"
NEWLINES = defaultdict(lambda: NEWLINE * 3)
NEWLINES["isort"] = NEWLINE * 2


class Index(NamedTuple):
    """Keep track of line and cell number while iterating over cells."""

    line_number: int
    cell_number: int


def _is_src_code_indentation_valid(source: str) -> bool:
    """
    Return True is the indentation of the input source code is valid.

    Parameters
    ----------
    source : str
        Source code present in the notebook cell

    Returns
    -------
    bool
        True if the source indentation is valid otherwise False
    """
    valid: bool = True
    try:
        ast.parse(source)
    except IndentationError:
        valid = False
    except SyntaxError:
        # Ignore any other exceptions. Let the syntax issues
        # be reported by the third party tool.
        pass

    return valid


def _handle_magic_indentation(
    source: Sequence[str], line_magic: str, magic_replacement: str
) -> str:
    """
    Handle the indentation of line magics. Remove unnecessary indentation.

    Parameters
    ----------
    source
        Source code of the notebook cell
    line_magic
        Line magic present in the notebook cell
    magic_replacement
        Python code replacing ipython magic
    Returns
    -------
    str
        Replacement line for the original line magic statement.
    """
    leading_space = "".join(takewhile(lambda c: c == " ", line_magic))

    # preserve the leading spaces and check if the syntax is valid
    replacement = indent(magic_replacement, leading_space)
    cell_source = "".join([*source, replacement])

    # If the cell contains multiple line magics `ast.parse` will raise
    # `SyntaxError`. Since we are interested in only checking the indentation
    # of the current line magic, previous line magics should be replaced with
    # some valid python token.
    # `%time print("hello")` will become `magic; print("hello")`
    cell_source = re.sub(r"%\w+", "magic;", cell_source)

    if leading_space and not _is_src_code_indentation_valid(cell_source):
        # Remove the line magic indentation assuming these leading spaces
        # lead the source to have invalid indentation
        # Currently we don't check if the original source
        # code itself had IndentationError
        replacement = magic_replacement

    if line_magic.endswith(NEWLINE):
        replacement += NEWLINE

    return replacement


def _extract_ipython_magic(magic: str, cell_source: Iterator[Tuple[int, str]]) -> str:
    r"""Extract the ipython magic from the notebook cell source.

    To extract ipython magic, we use `nbconvert.get_lines` because it can extract
    the ipython magic statement that can span multiple lines.

    .. code:: python

        # example of ipython magic spanning multiple lines
        %time result_pymc3 = eval_lda(\
        transform_pymc3, beta_pymc3, docs_te.toarray(), np.arange(100)\
        )

    `nbconvert.filters.get_lines` has the capability to parse such line magics and
    return the result as a single line with trailing backslash removed. `get_lines`
    would return `%time result_pymc3 = eval_lda(        transform_pymc3, beta_pymc3,
     docs_te.toarray(), np.arange(100)    )`

    If the magic was spanning multiple lines, then we need to remove all trailing
    backslashes introduced by previous runs of nbqa. Also we do need to preserve the
    newline characters, otherwise tools like black will format the code again. Linters
    like flake8, pylint will complain about line length. After we extract the code, we
    should have string like below

    .. code:: python

        %time result_pymc3 =eval_lda(
            transform_pymc3, beta_pymc3, docs_te.toarray(), np.arange(100)
        )

    Parameters
    ----------
    magic : str
        First line of the ipython magic

    cell_source: Iterator[Tuple[int, str]]
        Iterator to the notebook cell source

    Returns
    -------
    str
        IPython line magic statement
    """
    magic_type = MagicHandler.get_ipython_magic_type(magic)
    if magic_type and magic_type not in [IPythonMagicType.CELL, IPythonMagicType.HELP]:
        # Here we look for ipython magics spanning across multiple lines.
        while INPUT_SPLITTER.check_complete(magic)[0] == "incomplete":
            try:
                magic += next(cell_source)[1]
            except StopIteration:
                # This scenario is a syntax error where a line magic
                # ends with a backslash and does not have a next line.
                break

    return magic


def _replace_magics(
    source: Sequence[str], magic_substitutions: List[MagicHandler], command: str
) -> Iterator[str]:
    """
    Replace IPython line magics with valid python code.

    Parameters
    ----------
    source
        Source from notebook cell.
    magic_substitutions
        List to store all the ipython magics substitutions

    Yields
    ------
    str
        Line from cell, with line magics replaced with python code
    """
    source_itr = enumerate(source)
    for line_no, line in source_itr:
        if MagicHandler.is_ipython_magic(line):
            # always pass the source starting from the current line
            ipython_magic = _extract_ipython_magic(line, source_itr)
            magic_handler = MagicHandler.get_magic_handler(ipython_magic, command)
            magic_substitutions.append(magic_handler)
            line = _handle_magic_indentation(
                source[:line_no], ipython_magic, magic_handler.replace_magic()
            )

        yield line


def _parse_cell(
    source: Sequence[str],
    cell_number: int,
    temporary_lines: MutableMapping[int, Sequence[MagicHandler]],
    command: str,
) -> str:
    """
    Parse cell, replacing line magics with python code as placeholder.

    Parameters
    ----------
    source
        Source from notebook cell.
    cell_number
        Number identifying the notebook cell.
    temporary_lines
        Mapping to store the cell number to all the ipython magics replaced in those cells.
    command
        The third-party tool being run.

    Returns
    -------
    str
        Parsed cell.
    """
    substituted_magics: List[MagicHandler] = []
    parsed_cell = CODE_SEPARATOR

    for parsed_line in _replace_magics(source, substituted_magics, command):
        parsed_cell += parsed_line

    if substituted_magics:
        temporary_lines[cell_number] = substituted_magics

    return f"{parsed_cell}{NEWLINES[command]}"


def _get_line_numbers_for_mapping(
    cell_source: str, magic_substitutions: Sequence[MagicHandler]
) -> Mapping[int, int]:
    """Get the line number mapping from python file to notebook cell.

    Parameters
    ----------
    cell_source
        Source code of the notebook cell
    magic_substitutions
        IPython magics substituted in the current notebook cell.

    Returns
    -------
    Mapping[int, int]
        Line number mapping from temporary python file to notebook cell
    """
    lines_in_cell = cell_source.splitlines()
    line_mapping: MutableMapping[int, int] = {}

    if not magic_substitutions:
        line_mapping.update({i: i for i in range(len(lines_in_cell))})
    else:
        ignore_previous_line = False
        line_number = -1

        for line_no, line in enumerate(lines_in_cell):
            if ignore_previous_line:
                line_mapping[line_no] = line_number
                ignore_previous_line = False
                continue

            ignore_previous_line = any(
                magic_handler.should_ignore_for_line_mapping(line)
                for magic_handler in magic_substitutions
            )

            line_number += 1
            line_mapping[line_no] = line_number

    return line_mapping


def _should_ignore_code_cell(
    source: Sequence[str], process_cells: Sequence[str]
) -> bool:
    """
    Return True if the current cell should be ignored from processing.

    Parameters
    ----------
    source
        Source from the notebook cell
    process_cells
        Extra cells which nbqa should process.

    Returns
    -------
    bool
        True if the cell should ignored else False
    """
    if not source:
        return True
    process = MAGIC + [i.strip() for i in process_cells]
    magic_type = MagicHandler.get_ipython_magic_type(source[0])
    if magic_type != IPythonMagicType.CELL:
        return False
    first_line = source[0].lstrip()
    return first_line.split()[0] not in {f"%%{magic}" for magic in process}


def _has_trailing_semicolon(src: str) -> Tuple[str, bool]:
    """
    Check if cell has trailing semicolon.

    Parameters
    ----------
    src
        Notebook cell source.

    Returns
    -------
    bool
        Whether notebook has trailing semicolon.
    """
    tokens = tokenize_rt.src_to_tokens(src)
    trailing_semicolon = False
    for idx, token in tokenize_rt.reversed_enumerate(tokens):
        if not token.src.strip(" \n") or token.name == "COMMENT":
            continue
        if token.name == "OP" and token.src == ";":
            tokens[idx] = token._replace(src="")
            trailing_semicolon = True
        break
    if not trailing_semicolon:
        return src, False
    return tokenize_rt.tokens_to_src(tokens), True


def main(  # pylint: disable=R0914
    notebook: "Path",
    file_descriptor: int,
    process_cells: Sequence[str],
    command: str,
) -> NotebookInfo:
    """
    Extract code cells from notebook and save them in temporary Python file.

    Parameters
    ----------
    notebook
        Jupyter Notebook third-party tool is being run against.
    process_cells
        Extra cells which nbqa should process.
    command
        The third-party tool being run.

    Returns
    -------
    NotebookInfo

    """
    with open(str(notebook), encoding="utf-8") as handle:
        content = handle.read()

    cells = json.loads(content)["cells"]

    result = []
    cell_mapping = {0: "cell_0:0"}
    index = Index(line_number=0, cell_number=0)
    trailing_semicolons = set()
    temporary_lines: DefaultDict[int, Sequence[MagicHandler]] = defaultdict(list)
    code_cells_to_ignore = set()

    for cell in cells:
        if cell["cell_type"] == "code":
            index = index._replace(cell_number=index.cell_number + 1)

            if _should_ignore_code_cell(cell["source"], process_cells):
                code_cells_to_ignore.add(index.cell_number)
                continue

            parsed_cell = _parse_cell(
                cell["source"], index.cell_number, temporary_lines, command
            )

            cell_mapping.update(
                {
                    py_line
                    + index.line_number
                    + 1: f"cell_{index.cell_number}:{cell_line}"
                    for py_line, cell_line in _get_line_numbers_for_mapping(
                        parsed_cell, temporary_lines[index.cell_number]
                    ).items()
                }
            )
            parsed_cell, trailing_semicolon = _has_trailing_semicolon(parsed_cell)
            if trailing_semicolon:
                trailing_semicolons.add(index.cell_number)
            result.append(parsed_cell)
            index = index._replace(
                line_number=index.line_number + len(parsed_cell.splitlines())
            )

    result_txt = "".join(result).rstrip(NEWLINE) + NEWLINE if result else ""
    with open(file_descriptor, "w", encoding="utf-8") as handle:
        handle.write(result_txt)

    return NotebookInfo(
        cell_mapping, trailing_semicolons, temporary_lines, code_cells_to_ignore
    )
