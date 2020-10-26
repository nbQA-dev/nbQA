"""Detect ipython magics and provide python code replacements for those magics."""
import ast
import contextlib
import re
import secrets
from abc import ABC
from ast import AST
from typing import Optional, Pattern


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
    _token: str
    _ipython_magic: str

    def __init__(self, ipython_magic: str) -> None:
        self._token: str = MagicHandler._get_unique_token()
        self._ipython_magic = ipython_magic

    def replace_magic(self) -> str:
        """
        Return python code to replace the ipython magic.

        Returns
        -------
        str
            Python code to be substituted for the ipython magic
        """
        return self._MAGIC_TEMPLATE.format(magic=self._ipython_magic, token=self._token)

    def restore_magic(self, cell_source: str) -> str:
        pattern = MagicHandler._get_regex_pattern(
            self._MAGIC_REGEX_TEMPLATE, self._token
        )
        return re.sub(pattern, self._ipython_magic, cell_source)

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
            magic_handler = ShellCommandHandler(ipython_magic)
        elif ipython_magic[0] == "?" or ipython_magic[-1] == "?":
            magic_handler = HelpMagicHandler(ipython_magic)
        elif ipython_magic[0] == "%":
            if len(ipython_magic) > 1 and ipython_magic[1] == "%":
                magic_handler = CellMagicHandler(ipython_magic)
            else:
                magic_handler = LineMagicHandler(ipython_magic)

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

    _MAGIC_TEMPLATE_WITH_CODE: str = r"if int({token}):\n    {code}  # {token}"
    _MAGIC_WITH_CODE_REGEX_TEMPLATE: str = r"if\s+int\(\s*{token}\s*\).*{token}"
    _EXTRACT_CODE_REGEX_TEMPLATE: str = (
        r"if\s+int\(\s*{token}\s*\):\s+(.*)\s+#\s+{token}"
    )
    _contains_code: bool = False

    @staticmethod
    def _get_syntax_tree(stmt: str) -> Optional[AST]:
        syntax_tree: Optional[AST] = None
        with contextlib.suppress(SyntaxError):
            syntax_tree = ast.parse(stmt)

        return syntax_tree

    @staticmethod
    def _contains_callable(syntax_tree: AST) -> bool:
        """Return True if the syntax tree contains node of type `ast.Call`.

        Parameters
        ----------
        syntax_tree
            Python code parsed as Abstract Syntax Tree

        Returns
        -------
        bool
            True if the python code contains a callable
        """
        return any(isinstance(node, ast.Call) for node in ast.walk(syntax_tree))

    def replace_magic(self) -> str:
        """
        Return python code to be replace the input ipython magic.

        Returns
        -------
        str
            Python code to replace the ipython magic
        """
        # strip %line_magic_name from the line magic statement
        code: str = re.sub(r"%\w+", "", self._ipython_magic)
        syntax_tree = self._get_syntax_tree(code)
        if syntax_tree and self._contains_callable(syntax_tree):
            self._contains_code = True
            return self._MAGIC_TEMPLATE_WITH_CODE.format(code=code, token=self._token)

        return super().replace_magic()

    def restore_magic(self, cell_source: str) -> str:
        if self._contains_code:
            pattern = MagicHandler._get_regex_pattern(
                self._MAGIC_WITH_CODE_REGEX_TEMPLATE, self._token
            )
            return re.sub(
                pattern, self._extract_code(pattern, cell_source), cell_source
            )

        return super().restore_magic(cell_source)

    def _extract_code(
        self, replacement_code_pattern: Pattern[str], cell_source: str
    ) -> str:
        match_obj = replacement_code_pattern.search(cell_source)
        if match_obj:
            replaced_line = match_obj.group()
            # from the replaced line extract the python source code
            extract_code_pattern = MagicHandler._get_regex_pattern(
                self._EXTRACT_CODE_REGEX_TEMPLATE, self._token
            )
            match_obj = extract_code_pattern.search(replaced_line)
            if match_obj:
                extracted_code = match_obj.group(1)
                match_obj = re.match(r"%\w+", self._ipython_magic)
                if match_obj:
                    return f"{match_obj.group()} {extracted_code}".strip()

        # if not return the original source
        return self._ipython_magic
