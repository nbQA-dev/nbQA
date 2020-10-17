"""Detect ipython magics and provide python code replacements for those magics."""
import re
import secrets
from abc import ABC
from typing import Pattern, Tuple


class MagicSubstitution:
    """Store original ipython magic along with the replaced python code."""

    replacement_line: str
    _original_source: str
    _substitution_pattern: Pattern[str]

    def __init__(
        self, replacement_line: str, original_source: str, pattern: Pattern[str]
    ) -> None:
        """
        Initialize MagicSubstitution instance.

        Parameters
        ----------
        replacement_line : str
            Python code replacing the ipython magic
        original_source : str
            IPython magic present in the notebook cell
        pattern : Pattern[str]
            Regex pattern to restore the magic with python code
        """
        self.replacement_line = replacement_line
        self._original_source = original_source
        self._substitution_pattern = pattern

    def restore_magic(self, source: str) -> str:
        """
        Replace the original magic in the source.

        Parameters
        ----------
        source : str
            Source code of the notebook cell

        Returns
        -------
        str
            Source of the notebook cell with original ipython magic restored.
        """
        return re.sub(self._substitution_pattern, self._original_source, source)

    def indent_magic_replacement(self, spaces: str) -> str:
        """
        Indent the magic replacement code with the input leading spaces.

        Parameters
        ----------
        spaces : str
            Spaces to indent the replacement code.

        Returns
        -------
        str
            Indented replacement code
        """
        return f"{spaces}{self.replacement_line}"


class MagicHandler(ABC):
    """Base class of different types of magic handlers."""

    # Here token is placed at the beginning and at the end so that
    # the start and end of the code can be identified even if the code
    # is split across multiple lines.
    # `{token}` is not used as `String` because with different formatters (e.g: yapf)
    # we would run in to formatting issues like single quotes formatted
    # to double quotes or vice versa. `{token}` is used as hexadecimal number.
    _MAGIC_TEMPLATE: str = "type({token})  # {magic:10.10} {token}"
    _MAGIC_REGEX_TEMPLATE: str = r"type\s*\(\s*{token}\s*\).*{token}"

    def replace_magic(self, ipython_magic: str) -> MagicSubstitution:
        """
        Return python code to replace the ipython magic.

        Parameters
        ----------
        ipython_magic : str
            IPython magic statement present in the notebook cell

        Returns
        -------
        MagicSubstitution
            Python code to be substituted for the ipython magic
        """
        token: str = MagicHandler._get_unique_token()
        replacement_line, pattern = self._get_magic_replacement(token, ipython_magic)
        return MagicSubstitution(replacement_line, ipython_magic, pattern)

    def _get_magic_replacement(
        self, token: str, magic: str
    ) -> Tuple[str, Pattern[str]]:
        """
        Return python code to be replace the input ipython magic.

        Parameters
        ----------
        token : str
            Token to uniquely identify the replacement python code
        magic : str
            IPython magic statement

        Returns
        -------
        str
            Python code to replace the ipython magic
        """
        return (
            self._MAGIC_TEMPLATE.format(magic=magic, token=token),
            MagicHandler._get_regex_pattern(self._MAGIC_REGEX_TEMPLATE, token),
        )

    @staticmethod
    def _get_unique_token() -> str:
        """
        Return randomly generated token of hexadecimal characters.

        Returns
        -------
        str
            Token to uniquely identify the ipython magic replacement code.
        """
        return f"0x{int(secrets.token_hex(4), base=16):X}"

    @staticmethod
    def _get_regex_pattern(pattern_template: str, token: str) -> Pattern[str]:
        """
        Return the compiled regex pattern.

        Parameters
        ----------
        pattern_template : str
            Regex pattern for the magic replacement template
        token : str
            Token to uniquely identify the magic replacement

        Returns
        -------
        Pattern[str]
            Compiled regex pattern
        """
        return re.compile(pattern_template.format(token=token), re.RegexFlag.DOTALL)

    @staticmethod
    def is_ipython_magic(source: str) -> bool:
        """
        Return True if the source contains ipython magic.

        Parameters
        ----------
        source : str
            Source code present in the notebook cell.

        Returns
        -------
        bool
            True if the source contains ipython magic
        """
        return source.startswith(("!", "%", "?")) or source.endswith("?")

    @staticmethod
    def get_magic_handler(ipython_magic: str) -> "MagicHandler":
        """
        Return MagicHandler based on the type of ipython magic.

        Returns
        -------
        MagicHandler
            An instance of MagicHandler or some subclass of MagicHandler.
        """
        magic_handler: MagicHandler
        if ipython_magic[0] == "!":
            magic_handler = ShellCommandHandler()
        elif ipython_magic[0] == "?" or ipython_magic[-1] == "?":
            magic_handler = HelpMagicHandler()
        elif ipython_magic[0] == "%":
            if len(ipython_magic) > 1 and ipython_magic[1] == "%":
                magic_handler = CellMagicHandler()
            else:
                magic_handler = LineMagicHandler()

        return magic_handler


class HelpMagicHandler(MagicHandler):
    """Handle ipython magic starting or ending with ?."""


class ShellCommandHandler(MagicHandler):
    """Handle ipython magic containing !."""


class CellMagicHandler(MagicHandler):
    """Handle ipython magic starting with %%."""

    # We use a comment for replacing cell magic, since we don't want
    # cell magic statements to be formatted
    # For instance a cell magic placed above a function will be
    # formatted to be separated by two blank lines from the function
    # It would look odd to have a cell magic followed by blank lines.
    _MAGIC_TEMPLATE: str = "# CELL_MAGIC {magic:10.10} {token}"
    _MAGIC_REGEX_TEMPLATE: str = r"#\s*CELL_MAGIC.*{token}"


class LineMagicHandler(MagicHandler):
    """Handle ipython line magic starting with %."""
