"""Detect ipython magics and provide python code replacements for those magics."""
import secrets
from abc import ABC
from enum import Enum
from typing import *
import ast
from collections import defaultdict

from IPython.core.inputtransformer2 import TransformerManager

COMMANDS_WITH_STRING_TOKEN = {"flake8"}

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


class CellMagicFinder(ast.NodeVisitor):
    """Find assignments of system commands."""

    def __init__(self) -> None:
        """Record where system assigns occur."""
        self.header = None
        self.body = None

    def visit_Call(self, node: ast.Call):
        if _is_ipython_magic(node.func):
            assert isinstance(node.func, ast.Attribute)  # help mypy
            if node.func.attr == 'run_cell_magic':
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
                self.body = args[2].rstrip('\n')


class IPythonMagicType(Enum):
    """Enumeration representing various types of IPython magics."""

    SHELL = 0
    HELP = 1
    LINE = 2
    CELL = 3
    NO_MAGIC = 4


class NewMagicHandler:  # pylint: disable=R0903
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


class MagicHandler(ABC):  # pylint: disable=R0903
    """Base class of different types of magic handlers."""

    # To Developers: Its better to preserve the order in which
    # this dictionary is populated. For instance, if HELP is inserted
    # after LINE leads to bug, since they both share the same prefix.
    _MAGIC_PREFIXES: ClassVar[Mapping[IPythonMagicType, Sequence[str]]] = {
        IPythonMagicType.SHELL: ["get_ipython().system", "get_ipython().getoutput"],
        IPythonMagicType.HELP: ["get_ipython().run_line_magic('pinfo"],
        IPythonMagicType.LINE: ["get_ipython().run_line_magic", "get_ipython().magic"],
        IPythonMagicType.CELL: ["get_ipython().run_cell_magic"],
    }

    @staticmethod
    def get_ipython_magic_type(ipython_magic: str) -> Optional[IPythonMagicType]:
        """Return the type of ipython magic.

        This function assumes the input parameter to be a ipython magic. It is
        recommended to call this method after checking `is_ipython_magic`.

        Parameters
        ----------
        ipython_magic : str
            Ipython magic statement

        Returns
        -------
        Optional[IPythonMagicType]
            Type of the IPython magic
        """
        python_code = TransformerManager().transform_cell(ipython_magic)
        magic_type: Optional[IPythonMagicType] = None
        for magic, prefixes in MagicHandler._MAGIC_PREFIXES.items():
            if any(prefix in python_code for prefix in prefixes):
                magic_type = magic
                break
        else:
            magic_type = IPythonMagicType.NO_MAGIC

        return magic_type
