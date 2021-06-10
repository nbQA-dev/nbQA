"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import ast
import json
import secrets
from collections import defaultdict
from typing import (
    DefaultDict,
    List,
    Mapping,
    MutableMapping,
    NamedTuple,
    Sequence,
    Tuple,
)

import tokenize_rt
from IPython.core.inputtransformer2 import TransformerManager

from nbqa.handle_magics import (
    CellMagicFinder,
    MagicHandler,
    SystemAssignsFinder,
    Visitor,
)
from nbqa.notebook_info import NotebookInfo
from nbqa.path_utils import remove_prefix

CODE_SEPARATOR = f"# %%NBQA-CELL-SEP{secrets.token_hex(3)}\n"
MAGIC = frozenset(("time", "timeit", "capture", "pypy", "python", "python3"))
NEWLINE = "\n"
NEWLINES = defaultdict(lambda: NEWLINE * 3)
NEWLINES["isort"] = NEWLINE * 2


class Index(NamedTuple):
    """Keep track of line and cell number while iterating over cells."""

    line_number: int
    cell_number: int


def _process_source(
    source: str,
    command: str,
    magic_substitutions: List[MagicHandler],
    *,
    skip_bad_cells: bool,
) -> str:
    """Temporarily replace ipython magics - don't process if can't."""
    try:
        ast.parse(source)
    except SyntaxError:
        pass
    else:
        # Source has no IPython magic, return it directly
        return source
    body = TransformerManager().transform_cell(source)
    if len(body.splitlines()) != len(source.splitlines()):
        handler = MagicHandler(source, command, magic_type=None)
        magic_substitutions.append(handler)
        return handler.replacement
    try:
        tree = ast.parse(body)
    except SyntaxError:
        if skip_bad_cells:
            handler = MagicHandler(source, command, magic_type=None)
            magic_substitutions.append(handler)
            return handler.replacement
        return source
    system_assigns_finder = SystemAssignsFinder()
    system_assigns_finder.visit(tree)
    visitor = Visitor(system_assigns_finder.system_assigns)
    visitor.visit(tree)
    new_src = []
    for i, line in enumerate(body.splitlines(), start=1):
        if i in visitor.magics:
            col_offset, src, magic_type = visitor.magics[i][0]
            if src is None or len(visitor.magics[i]) > 1:
                # unusual case - skip cell completely for now
                handler = MagicHandler(source, command, magic_type=magic_type)
                magic_substitutions.append(handler)
                return handler.replacement
            handler = MagicHandler(
                src,
                command,
                magic_type=magic_type,
            )
            magic_substitutions.append(handler)
            line = line[:col_offset] + handler.replacement
        new_src.append(line)
    return "\n" * (len(source) - len(source.lstrip("\n"))) + "\n".join(new_src)


def _replace_magics(
    source: Sequence[str],
    magic_substitutions: List[MagicHandler],
    command: str,
    *,
    skip_bad_cells: bool,
) -> str:
    """
    Replace IPython line magics with valid python code.

    Parameters
    ----------
    source
        Source from notebook cell.
    magic_substitutions
        List to store all the ipython magics substitutions

    Returns
    -------
    str
        Line from cell, with line magics replaced with python code
    """
    try:
        ast.parse("".join(source))
    except SyntaxError:
        pass
    else:
        # Source has no IPython magic, return it directly
        return "".join(source)

    cell_magic_finder = CellMagicFinder()
    body = TransformerManager().transform_cell("".join(source))
    try:
        tree = ast.parse(body)
    except SyntaxError:
        if skip_bad_cells:
            handler = MagicHandler("".join(source), command, magic_type=None)
            magic_substitutions.append(handler)
            return handler.replacement
        return "".join(source)
    cell_magic_finder.visit(tree)

    # if first line is cell magic, process it separately
    if cell_magic_finder.header is not None:
        assert cell_magic_finder.body is not None
        header = _process_source(
            cell_magic_finder.header,
            command,
            magic_substitutions,
            skip_bad_cells=skip_bad_cells,
        )
        cell = _process_source(
            cell_magic_finder.body,
            command,
            magic_substitutions,
            skip_bad_cells=skip_bad_cells,
        )
        return "\n".join([header, cell])

    return _process_source(
        "".join(source), command, magic_substitutions, skip_bad_cells=skip_bad_cells
    )


def _parse_cell(
    source: Sequence[str],
    cell_number: int,
    temporary_lines: MutableMapping[int, Sequence[MagicHandler]],
    command: str,
    *,
    skip_bad_cells: bool,
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

    parsed_cell += _replace_magics(
        source, substituted_magics, command, skip_bad_cells=skip_bad_cells
    )

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
        line_number = -1

        for line_no, _ in enumerate(lines_in_cell):
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
    if not "".join(source):
        return True

    try:
        ast.parse("".join(source))
    except SyntaxError:
        # Deal with this below
        pass
    else:
        # No need to ignore
        return False

    cell_magic_finder = CellMagicFinder()
    body = TransformerManager().transform_cell("".join(source))
    try:
        tree = ast.parse(body)
    except SyntaxError:
        # Don't ignore, let tool deal with syntax error
        return False
    cell_magic_finder.visit(tree)

    if cell_magic_finder.header is None:
        # If there's no cell magic, don't ignore.
        return False
    magic_name = remove_prefix(cell_magic_finder.header.split()[0], "%%")
    return magic_name not in MAGIC and magic_name not in {
        i.strip() for i in process_cells
    }


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
    notebook: str,
    file_descriptor: int,
    process_cells: Sequence[str],
    command: str,
    *,
    skip_bad_cells: bool,
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
                cell["source"],
                index.cell_number,
                temporary_lines,
                command,
                skip_bad_cells=skip_bad_cells,
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
