"""Detect ipython magics and provide python code replacements for those magics."""
import ast
import contextlib
import re
import secrets
import sys
import warnings
from abc import ABC
from ast import AST
from enum import Enum
from textwrap import dedent, indent
from typing import ClassVar, Mapping, Optional, Pattern, Sequence

with warnings.catch_warnings():
    # see https://github.com/nbQA-dev/nbQA/issues/459
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from IPython.core.inputsplitter import IPythonInputSplitter


INPUT_SPLITTER = IPythonInputSplitter(line_input_checker=False)

COMMANDS_WITH_STRING_TOKEN = {"flake8"}


class IPythonMagicType(Enum):
    """Enumeration representing various types of IPython magics."""

    SHELL = 0
    HELP = 1
    LINE = 2
    CELL = 3
    NO_MAGIC = 4


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

    # To Developers: Its better to preserve the order in which
    # this dictionary is populated. For instance, if HELP is inserted
    # after LINE leads to bug, since they both share the same prefix.
    _MAGIC_PREFIXES: ClassVar[Mapping[IPythonMagicType, Sequence[str]]] = {
        IPythonMagicType.SHELL: ["get_ipython().system", "get_ipython().getoutput"],
        IPythonMagicType.HELP: ["get_ipython().run_line_magic('pinfo"],
        IPythonMagicType.LINE: ["get_ipython().run_line_magic", "get_ipython().magic"],
        IPythonMagicType.CELL: ["get_ipython().run_cell_magic"],
    }

    def __init__(self, ipython_magic: str, command: str) -> None:
        """Initialize this instance.

        Parameters
        ----------
        ipython_magic : str
            Ipython magic statement present in the notebook cell
        """
        self._ipython_magic = ipython_magic
        self._command = command
        self._token: str = MagicHandler._get_unique_token(command)

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

    def should_ignore_for_line_mapping(self, _: str) -> bool:  # pylint: disable=R0201
        """Return True if the line should be ignored from line mapping.

        Parameters
        ----------
        _ : str
            Line to check

        Returns
        -------
        bool
            True if the line should be ignored. False otherwise
        """
        return False

    @staticmethod
    def _get_unique_token(command: str) -> str:
        """
        Return randomly generated token of hexadecimal characters.

        Returns
        -------
        str
            Token to uniquely identify the ipython magic replacement code.
        """
        token = secrets.token_hex(4)
        if command in COMMANDS_WITH_STRING_TOKEN:
            return f'"{token}"'
        return f"0x{int(token, base=16):X}"

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

        A statement like ``%%timeit get_ipython().run_line_magic("magic", "input")``
        already contains ``get_ipython()`` function call. To handle such cases, we need
        to check if the original source itself contains any ``get_ipython()`` function
        call before concluding the statement is an ipython magic.

        A statement like ``some_result = str.split??`` gets transformed into two
        python statements when using ``IPythonInputSplitter.transform_cell``. Thus we
        need to check if the count is more than the count on the input source.

        Parameters
        ----------
        source : str
            Source code present in the notebook cell.

        Returns
        -------
        bool
            True if the source contains ipython magic
        """
        src_count = source.count("get_ipython()")
        get_ipython_count: int = INPUT_SPLITTER.transform_cell(source).count(
            "get_ipython()"
        )
        return get_ipython_count > src_count

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
        python_code = INPUT_SPLITTER.transform_cell(ipython_magic)
        magic_type: Optional[IPythonMagicType] = None
        for magic, prefixes in MagicHandler._MAGIC_PREFIXES.items():
            if any(prefix in python_code for prefix in prefixes):
                magic_type = magic
                break
        else:
            magic_type = IPythonMagicType.NO_MAGIC

        return magic_type

    @staticmethod
    def preprocess_ipython_magic(ipython_magic: str) -> str:
        r"""
        Remove leading and trailing spaces, trailing slashes from ipython magic.

        If the trailing slashes are present in ipython magic(its an incomplete magic),
        then we would have issues with ``re.sub`` when replacing the ipython magic back
        to the cell source. ``re.compile("something ending with slash\\")`` will fail to
        compile. By stripping trailing slashes, the regex would compile fine during
        substitution.

        Parameters
        ----------
        ipython_magic : str
            IPython magic

        Returns
        -------
        str
            IPython magic stripped of spaces and trailing slashes
        """
        ipython_magic = dedent(ipython_magic).strip()
        if INPUT_SPLITTER.check_complete(ipython_magic)[0] == "incomplete":
            ipython_magic = ipython_magic.rstrip("\\")

        return ipython_magic

    @staticmethod
    def get_magic_handler(ipython_magic: str, command: str) -> "MagicHandler":
        """
        Return MagicHandler based on the type of ipython magic.

        Returns
        -------
        MagicHandler
            An instance of MagicHandler or some subclass of MagicHandler.
        """
        ipython_magic = MagicHandler.preprocess_ipython_magic(ipython_magic)
        magic_type = MagicHandler.get_ipython_magic_type(ipython_magic)

        magic_handler: MagicHandler
        if magic_type == IPythonMagicType.SHELL:
            magic_handler = ShellCommandHandler(ipython_magic, command)
        elif magic_type == IPythonMagicType.HELP:
            magic_handler = HelpMagicHandler(ipython_magic, command)
        elif magic_type == IPythonMagicType.CELL:
            magic_handler = CellMagicHandler(ipython_magic, command)
        else:
            # make this as the default case
            magic_handler = LineMagicHandler(ipython_magic, command)

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
    """Handle ipython line magic starting with ``%``.

    When ipython magic like ``%time`` that can contain python code, if we ignore the
    code and replace the line magic with the template ``type(hex_token)...``, we will
    get into a scenario of unused imports.

    For example, consider the following snippet.

    .. code:: python

        import os

        if True:
            %time os.system("ls -l")

    In the above snippet, if we replace the ``%time`` line magic with ``type(token)  #``
    statement, then flake8 or pylint would complain ``unused import os``. Also tools
    like autoflake would remove those statements from the notebook which is undesirable.

    To handle this issue, we transform the above snippet to a temporary python code that
    looks like the snippet below

    .. code:: python

        import os

        if True:
            if int(hex_token):
                os.system("ls -l")  # hex_token

    Before transforming the line magic to the above form, first the line magic is
    checked if it contains any python code with a callable. Otherwise the usual
    template is used. For instance line magics like ``%load_ext`` won't contain any
    python code. So such line magics will be replaced with ``type(hex_token)`` template.

    Now till this change the linters are happy. But there will be a problem with code
    formatters like black. Consider the below snippet

    .. code:: python

        %time func(arg1,arg2)

    This line magic will be transformed and after black formatting the code will look as

    .. code:: python

        if int(hex_token):
            func(arg1, arg2)  # hex_token

    Note ``func(arg1, arg2)`` got formatted. If we don't replace this newly formatted
    code back to original notebook cell source, every time black will reformat this
    notebook and we might have failures from tools like pre-commit.

    To avoid this issue, we need to extract only the formatted source
    ``func(arg1, arg2)`` and add it to ``%time``, and then restore this new statement
    back to the cell source. This logic is done in the method ``_restore_magic_with_modified_code``.
    """

    _MAGIC_TEMPLATE_WITH_CODE: str = dedent(
        """
        if int({token}):
        {indented_code}  # {token}
        """
    ).strip()
    _MAGIC_WITH_CODE_REGEX_TEMPLATE: str = r"if\s+int\(\s*{token}\s*\).*{token}"
    _EXTRACT_CODE_REGEX_TEMPLATE: str = (
        r"if\s+int\(\s*{token}\s*\):\s+(.*)\s+#\s+{token}"
    )
    _LEADING_SPACES: str = " " * 4

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
        code: str = dedent(
            re.sub(r"%\w+", lambda m: " " * len(m.group()), self._ipython_magic)
        ).strip()
        syntax_tree = self._get_syntax_tree(code)
        if syntax_tree and self._contains_callable(syntax_tree):
            self._contains_code = True
            # remove the trailing backslashes if any from the code
            code = re.sub(r"\\\n", "\n", code)
            return self._MAGIC_TEMPLATE_WITH_CODE.format(
                indented_code=indent(code, self._LEADING_SPACES), token=self._token
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

        # In case of any assertion failures, we should gracefully handle it
        # by replacing the temporary python code with the original ipython magic
        # Hence AssertionError is caught and ignored.
        try:
            # Get the code used for replacing the ipython magic statement
            match_obj = replacement_code_pattern.search(cell_source)
            if match_obj is None:  # pragma: nocover
                raise AssertionError(
                    "Unable to extract the python code substituted for ipython magic"
                )

            extracted_code = self._extract_code(match_obj.group())

            # IPython magic is recreated from modified source so that formatters
            # like black won't reformat the notebook every time they are run.
            ipython_magic = (
                f"{self._extract_line_magic()} "
                f"{self._indent_extracted_code(extracted_code)}"
            )
        except AssertionError as err:  # pragma: nocover
            sys.stderr.write(
                dedent(
                    f"""
                    Warning! Unable to process ipython magic `{self._ipython_magic}`
                    Exception message: {str(err)}. If this warnings persists across
                    multiple executions, please report a bug at
                    https://github.com/nbQA-dev/nbQA/issues.
                    """
                )
            )

        return replacement_code_pattern.sub(ipython_magic, cell_source)

    def _extract_code(self, replacement_code: str) -> str:
        """Extract the python code that was present in original ipython magic.

        Line magic like ``%time func(a, b)`` will get replaced in the temporary python
        as file as

        .. code:: python

            if int(some_hex_token):
                func(a, b)  # some_hex_token

        This method extracts only ``func(a, b)`` from the above python code. This
        extracted code will be written to the original notebook. This is done so that
        changes made by formatters on those pieces of code are captured and thereby
        preventing formatters like black reformatting the notebook every time they are
        run on the notebook.

        Parameters
        ----------
        replacement_code : str
            Python code used for replacing the line magic

        Returns
        -------
        str
            Extracted python code

        Raises
        ------
        AssertionError
            Raised when unable to extract the python code
        """
        # from the replaced code extract the python source code
        # that was also present in the original ipython magic
        extract_code_pattern = MagicHandler._get_regex_pattern(
            self._EXTRACT_CODE_REGEX_TEMPLATE, self._token
        )
        match_obj = extract_code_pattern.search(replacement_code)
        if match_obj is None:  # pragma: nocover
            raise AssertionError("Unable to extract code from the replaced python code")
        # This is needed because if formatters like black break the code in to many
        # lines, when the current statement exceeds the configured line length.
        # But ipython syntax requires multiline line magics to end with a backslash
        # By adding `\` to end of each line, line magic spanning multiple lines is
        # parsed as single line by jupyter/ipython.
        # For example, black formatted code like below
        # %time np.random.randn(
        #           100
        #       )
        # will become
        # %time np.random.randn(\
        #           100\
        #       )
        return re.sub("\n", "\\\n", match_obj.group(1))

    def _extract_line_magic(self) -> str:
        """Extract only the line magic of the format ``%<magic_name>``.

        Returns
        -------
        str
            Returns the line magic from the original source code.

        Raises
        ------
        AssertionError
            Raised if unable to extract the line magic from the source.
        """
        match_obj = re.match(r"%\w+", self._ipython_magic)
        if match_obj is None:  # pragma: nocover
            raise AssertionError("Unable to extract the line magic")
        return match_obj.group()

    @staticmethod
    def _indent_extracted_code(extracted_code: str) -> str:
        """Return the extracted code indented by 2 spaces.

        Code is indented by exactly 2 spaces, so that code like below

        .. code:: python

            %time np.random.randn(\
                    1000\
                )

        will look aesthetically better like below

        .. code:: python

            %time np.random.randn(\
                    1000\
                )

        Parameters
        ----------
        extracted_code : str
            Python code extracted from the modified source in temporary python file

        Returns
        -------
        str
            Indented python code
        """
        return indent(extracted_code, prefix=" " * 2).strip()

    def should_ignore_for_line_mapping(self, line: str) -> bool:
        """Return True if the line should be ignored from line mapping.

        Parameters
        ----------
        line : str
            Line to check

        Returns
        -------
        bool
            True if the line should be ignored. False otherwise
        """
        return (
            re.fullmatch(rf"\s*if\s+int\(\s*{self._token}\s*\):\s*", line, re.DOTALL)
            is not None
        )
