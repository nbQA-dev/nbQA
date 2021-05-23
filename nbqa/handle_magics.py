"""Detect ipython magics and provide python code replacements for those magics."""
import secrets
from abc import ABC
from enum import Enum
from typing import ClassVar, Mapping, Optional, Sequence

from IPython.core.inputtransformer2 import TransformerManager

COMMANDS_WITH_STRING_TOKEN = {"flake8"}


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
            self.replacement = f"str({self.token})"


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
