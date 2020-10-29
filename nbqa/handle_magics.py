"""Detect ipython magics and provide python code replacements for those magics."""
import ast
import contextlib
import re
import secrets
from abc import ABC
from ast import AST
from textwrap import dedent, indent
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
        """Initialize this instance.

        Parameters
        ----------
        ipython_magic : str
            Ipython magic statement present in the notebook cell
        """
        self._ipython_magic = ipython_magic
        self._token: str = MagicHandler._get_unique_token()

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
        """Return the cell source with the ipython magic restored.

        Parameters
        ----------
        cell_source : str
            Source code of the notebook cell

        Returns
        -------
        str
            Cell source with ipython magic restored.
        """
        pattern = MagicHandler._get_regex_pattern(
            self._MAGIC_REGEX_TEMPLATE, self._token
        )
        return pattern.sub(self._ipython_magic, cell_source)

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
        return source.strip().startswith(("!", "%", "?")) or source.endswith("?")

    @staticmethod
    def get_magic_handler(ipython_magic: str) -> "MagicHandler":
        """
        Return MagicHandler based on the type of ipython magic.

        Returns
        -------
        MagicHandler
            An instance of MagicHandler or some subclass of MagicHandler.
        """
        ipython_magic = ipython_magic.strip()
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
    """Handle ipython line magic starting with %.

    Description
    -----------
    When ipython magic like `%time` that can contain python code, if we ignore the
    code and replace the line magic with the template `type(hex_token)...`, we will
    get into a scenario of unused imports.

    For example, consider the following snippet.

    ```Python
    import os

    if True:
        %time os.system("ls -l")
    ```

    In the above snippet, if we replace the `%time` line magic with `type(token)  #`
    statement, then flake8 or pylint would complain `unused import os`. Also tools
    like autoflake would remove those statements from the notebook which is undesirable.

    To handle this issue, we transform the above snippet to a temporary python code that
    looks like the snippet below

    ```Python
    import os

    if True:
        if int(hex_token):
            os.system("ls -l")  # hex_token
    ```

    Before transforming the line magic to the above form, first the line magic is
    checked if it contains any python code with a callable. Otherwise the usual
    template is used. For instance line magics like `%load_ext` won't contain any
    python code. So such line magics will be replaced with `type(hex_token)` template.

    Now till this change the linters are happy. But there will be a problem with code
    formatters like black. Consider the below snippet

    ```Python
    %time func(arg1,arg2)
    ```

    This line magic will be transformed and after black formatting the code will look as

    ```Python
    if int(hex_token):
        func(arg1, arg2)  # hex_token
    ```

    Note `func(arg1, arg2)` got formatted. If we don't replace this newly formatted
    code back to original notebook cell source, every time black will reformat this
    notebook and we might have failures from tools like pre-commit.

    To avoid this issue, we need to extract only the formatted source `func(arg1, arg2)`
    and add it to `%time`, and then restore this new statement back to the cell source.
    This logic is done in the method `_restore_magic_with_modified_code`.
    """

    _MAGIC_TEMPLATE_WITH_CODE: str = dedent(
        """
        if int({token}):
        {code}  # {token}
        """
    ).strip()
    _MAGIC_WITH_CODE_REGEX_TEMPLATE: str = r"if\s+int\(\s*{token}\s*\).*{token}"
    _EXTRACT_CODE_REGEX_TEMPLATE: str = (
        r"if\s+int\(\s*{token}\s*\):\s+(.*)\s+#\s+{token}"
    )

    _contains_code: bool = False

    @staticmethod
    def _get_syntax_tree(stmt: str) -> Optional[AST]:
        """Return the input statement parsed as AST.

        Parameters
        ----------
        stmt : str
            String to be parsed by `ast.parse`

        Returns
        -------
        Optional[AST]
            Return AST if the statement is a valid python code else None
        """
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
        # Remove %line_magic from the line magic statement
        # Remove leading indentation and remove leading and trailing spaces
        code: str = dedent(re.sub(r"%\w+", " " * 4, self._ipython_magic)).strip()
        syntax_tree = self._get_syntax_tree(code)
        if syntax_tree and self._contains_callable(syntax_tree):
            self._contains_code = True
            return self._MAGIC_TEMPLATE_WITH_CODE.format(
                code=indent(code, " " * 4), token=self._token
            )

        return super().replace_magic()

    def restore_magic(self, cell_source: str) -> str:
        """Return the cell source with the ipython magic restored.

        Parameters
        ----------
        cell_source : str
            Source code of the notebook cell

        Returns
        -------
        str
            Cell source with ipython magic restored.
        """
        if self._contains_code:
            pattern = MagicHandler._get_regex_pattern(
                self._MAGIC_WITH_CODE_REGEX_TEMPLATE, self._token
            )
            return self._restore_magic_with_modified_code(pattern, cell_source)

        return super().restore_magic(cell_source)

    def _restore_magic_with_modified_code(
        self, replacement_code_pattern: Pattern[str], cell_source: str
    ) -> str:
        """Return cell source code with ipython magic statement restored.

        Parameters
        ----------
        replacement_code_pattern : Pattern[str]
            Regex pattern to find the python code replacing the ipython magic
        cell_source : str
            Source code of the notebook cell

        Returns
        -------
        str
            Cell source with ipython magic restored
        """
        ipython_magic = self._ipython_magic
        with contextlib.suppress(AssertionError):
            # Get the code used for replacing the ipython magic statement
            match_obj = replacement_code_pattern.search(cell_source)
            assert match_obj is not None
            replacement_code = match_obj.group()

            # from the replaced code extract the python source code
            # that was also present in the original ipython magic
            extract_code_pattern = MagicHandler._get_regex_pattern(
                self._EXTRACT_CODE_REGEX_TEMPLATE, self._token
            )
            match_obj = extract_code_pattern.search(replacement_code)
            assert match_obj is not None
            # This is needed because if formatters like black format the code
            # to span across multiple lines, then we need to add \ to end of each line
            # so that line magic parses all those lines as part of one python statement.
            # %time np.random.randn(\
            # 100\
            # )
            extracted_code = re.sub("\n", "\\\n", match_obj.group(1))

            # combine %line_magic and the extracted code to be the new
            # ipython magic statement.
            # This is done so that formatters like black won't reformat the notebook
            # every time they are run on the notebook.
            match_obj = re.match(r"%\w+", self._ipython_magic)
            assert match_obj is not None
            ipython_magic = f"{match_obj.group()} {extracted_code}".strip()

        return replacement_code_pattern.sub(ipython_magic, cell_source)
