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
    Iterator,
    List,
    Mapping,
    MutableMapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
)

import tokenize_rt
from IPython.core.inputtransformer2 import TransformerManager

from nbqa.handle_magics import IPythonMagicType, MagicHandler, NewMagicHandler
from nbqa.notebook_info import NotebookInfo

CODE_SEPARATOR = f"# %%NBQA-CELL-SEP{secrets.token_hex(3)}\n"
MAGIC = ["time", "timeit", "capture", "pypy", "python", "python3"]
NEWLINE = "\n"
NEWLINES = defaultdict(lambda: NEWLINE * 3)
NEWLINES["isort"] = NEWLINE * 2


class Index(NamedTuple):
    """Keep track of line and cell number while iterating over cells."""

    line_number: int
    cell_number: int


def _is_ipython_magic(node: ast.expr) -> bool:
    """Check if attribute is IPython magic."""
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "get_ipython"
    )


class SystemAssignsFinder(ast.NodeVisitor):
    """Find assignments of system commands."""

    def __init__(self) -> None:
        """Record where system assigns occur."""
        self.system_assigns: Set[Tuple[int, int]] = set()

    def visit_Assign(self, node: ast.Assign) -> None:  # pylint: disable=C0103
        """Find assignments of ipython magic."""
        if isinstance(node.value, ast.Call) and _is_ipython_magic(node.value.func):
            self.system_assigns.add((node.value.lineno, node.value.col_offset))

        self.generic_visit(node)


class Visitor(ast.NodeVisitor):
    """Visit cell to look for get_ipython calls."""

    def __init__(self, system_assigns: Set[Tuple[int, int]]) -> None:
        """Magics will record where magics occur."""
        self.magics: MutableMapping[
            int, List[Tuple[int, Optional[str], Optional[str]]]
        ] = defaultdict(list)
        self.system_assigns = system_assigns

    def visit_Call(self, node: ast.Call) -> None:  # pylint: disable=C0103,R0912
        """
        Get source to replace ipython magic with.

        Parameters
        ----------
        node
            Function call.

        Raises
        ------
        AssertionError
            Defensive check.
        """
        if _is_ipython_magic(node.func):
            assert isinstance(node.func, ast.Attribute)  # help mypy
            args = []
            for arg in node.args:
                if isinstance(arg, ast.Str):
                    args.append(arg.s)
                else:
                    raise AssertionError(
                        "Please report a bug at https://github.com/nbQA-dev/nbQA/issues"
                    )
            assert (
                args
            ), "Please report a bug at https://github.com/nbQA-dev/nbQA/issues"
            magic_type: Optional[str] = None
            if node.func.attr == "run_cell_magic":
                src: Optional[str] = f"%%{args[0]}"
                if args[1]:
                    assert src is not None
                    src += f" {args[1]}"
                magic_type = "cell"
            elif node.func.attr == "run_line_magic":
                if args[0] == "pinfo":
                    src = f"{args[1]}?"
                elif args[0] == "pinfo2":
                    src = f"{args[1]}??"
                else:
                    src = f"%{args[0]}"
                    if args[1]:
                        assert src is not None
                        src += f" {args[1]}"
                magic_type = "line"
            elif node.func.attr == "system":
                src = f"!{args[0]}"
                magic_type = "line"
            elif node.func.attr == "getoutput":
                if (node.lineno, node.col_offset) in self.system_assigns:
                    src = f"!{args[0]}"
                else:
                    src = f"!!{args[0]}"
                magic_type = "line"
            else:
                src = None
            self.magics[node.lineno].append(
                (
                    node.col_offset,
                    src,
                    magic_type,
                )
            )
        self.generic_visit(node)


def _process_source(
    source: str,
    command: str,
    magic_substitutions: List[NewMagicHandler],
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
        handler = NewMagicHandler(source, command, magic_type=None)
        magic_substitutions.append(handler)
        return handler.replacement
    try:
        tree = ast.parse(body)
    except SyntaxError:
        if skip_bad_cells:
            handler = NewMagicHandler(source, command, magic_type=None)
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
                handler = NewMagicHandler(source, command, magic_type=magic_type)
                magic_substitutions.append(handler)
                return handler.replacement
            handler = NewMagicHandler(
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
    magic_substitutions: List[NewMagicHandler],
    command: str,
    *,
    skip_bad_cells: bool,
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
    # if first line is cell magic, process it separately
    if MagicHandler.get_ipython_magic_type(source[0]) == IPythonMagicType.CELL:
        header = _process_source(
            source[0], command, magic_substitutions, skip_bad_cells=skip_bad_cells
        )
        cell = _process_source(
            "".join(source[1:]),
            command,
            magic_substitutions,
            skip_bad_cells=skip_bad_cells,
        )
        yield "\n".join([header, cell])
    else:
        yield _process_source(
            "".join(source), command, magic_substitutions, skip_bad_cells=skip_bad_cells
        )


def _parse_cell(
    source: Sequence[str],
    cell_number: int,
    temporary_lines: MutableMapping[int, Sequence[NewMagicHandler]],
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
    substituted_magics: List[NewMagicHandler] = []
    parsed_cell = CODE_SEPARATOR

    for parsed_line in _replace_magics(
        source, substituted_magics, command, skip_bad_cells=skip_bad_cells
    ):
        parsed_cell += parsed_line

    if substituted_magics:
        temporary_lines[cell_number] = substituted_magics

    return f"{parsed_cell}{NEWLINES[command]}"


def _get_line_numbers_for_mapping(
    cell_source: str, magic_substitutions: Sequence[NewMagicHandler]
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
    temporary_lines: DefaultDict[int, Sequence[NewMagicHandler]] = defaultdict(list)
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
