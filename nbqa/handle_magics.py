"""Detect ipython magics and provide python code replacements for those magics."""
import ast
import secrets
from collections import defaultdict
from typing import List, MutableMapping, Optional, Tuple

COMMANDS_WITH_STRING_TOKEN = {"flake8"}


def _is_ipython_magic(node: ast.expr) -> bool:
    """Check if attribute is IPython magic."""
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "get_ipython"
    )


class Visitor(ast.NodeVisitor):
    """Visit cell to look for get_ipython calls."""

    def __init__(self) -> None:
        """Magics will record where magics occur."""
        self.magics: MutableMapping[
            int, List[Tuple[int, Optional[str], Optional[str]]]
        ] = defaultdict(list)

    def visit_Assign(self, node: ast.Assign) -> None:  # pylint: disable=C0103,R0912
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
        if (
            isinstance(node.value, ast.Call)
            and _is_ipython_magic(node.value.func)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "getoutput"
        ):
            args = []
            for arg in node.value.args:
                if isinstance(arg, ast.Str):
                    args.append(arg.s)
                else:
                    raise AssertionError(
                        "Please report a bug at https://github.com/nbQA-dev/nbQA/issues"
                    )
            assert (
                args
            ), "Please report a bug at https://github.com/nbQA-dev/nbQA/issues"
            src = f"!{args[0]}"
            magic_type = "line"
            self.magics[node.value.lineno].append(
                (
                    node.value.col_offset,
                    src,
                    magic_type,
                )
            )
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:  # pylint: disable=C0103,R0912
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
        if isinstance(node.value, ast.Call) and _is_ipython_magic(node.value.func):
            assert isinstance(node.value.func, ast.Attribute)  # help mypy
            args = []
            for arg in node.value.args:
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
            if node.value.func.attr == "run_cell_magic":
                src: Optional[str] = f"%%{args[0]}"
                if args[1]:
                    assert src is not None
                    src += f" {args[1]}"
                magic_type = "cell"
            elif node.value.func.attr == "run_line_magic":
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
            elif node.value.func.attr == "system":
                src = f"!{args[0]}"
                magic_type = "line"
            elif node.value.func.attr == "getoutput":
                src = f"!!{args[0]}"
                magic_type = "line"
            else:
                src = None
            self.magics[node.value.lineno].append(
                (
                    node.value.col_offset,
                    src,
                    magic_type,
                )
            )
        self.generic_visit(node)


class CellMagicFinder(ast.NodeVisitor):
    """Find cell magics."""

    def __init__(self) -> None:
        """Record where cell magics occur."""
        self.header: Optional[str] = None
        self.body: Optional[str] = None

    def visit_Call(self, node: ast.Call) -> None:  # pylint: disable=C0103
        """
        Find cell magic, extract header and body.

        Raises
        ------
        AssertionError
            Defensive check.
        """
        if _is_ipython_magic(node.func):
            assert isinstance(node.func, ast.Attribute)  # help mypy
            if node.func.attr == "run_cell_magic":
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Str):
                        args.append(arg.s)
                    else:
                        raise AssertionError(
                            "Please report a bug at https://github.com/nbQA-dev/nbQA/issues"
                        )
                header: Optional[str] = f"%%{args[0]}"
                if args[1]:
                    assert header is not None
                    header += f" {args[1]}"
                self.header = header
                self.body = args[2].rstrip("\n")


class MagicHandler:  # pylint: disable=R0903
    """Handle different types of magics."""

    def __init__(self, src: str, command: str, magic_type: Optional[str]):
        """
        Handle magic.

        Parameters
        ----------
        src
            Original code
        command
            e.g. flake8
        magic_type
            E.g. cell, line, ...
        """
        self.src = src
        token = secrets.token_hex(4)
        if command in COMMANDS_WITH_STRING_TOKEN:
            self.token = f'"{token}"'
        else:
            self.token = f"0x{int(token, base=16):X}"
        if magic_type == "cell":
            self.replacement = f"# CELL MAGIC {self.token}"
        else:
            self.replacement = f"hash({self.token})"
