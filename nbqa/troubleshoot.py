"""Check if nbqa can find the command in its PATH."""
import sys
from importlib.machinery import ModuleSpec
from importlib.util import find_spec
from pathlib import Path
from textwrap import dedent

_COMMAND_FOUND_TEMPLATE = dedent(
    """\
    {command} is found by nbqa at "{command_loc}" !
"""
)

_COMMAND_NOT_FOUND_TEMPLATE = dedent(
    """\
    {command} cannot be found by nbqa.
    Python executable: {python}
    nbqa location: {nbqa_loc}

    It seems {command} is not installed in the same python environment as nbqa.
    Please run `{python} -m pip install {command}` so that nbqa can find {command}.

    To install nbqa in a python virtual environment please refer to
    https://nbqa.readthedocs.io/en/latest/readme.html#installation
    """
)


def find_command(command: str) -> int:
    """Inspect if nbqa is able to locate the command passed.

    Parameters
    ----------
    command : str
        Third party tool to be found by nbqa.

    Returns
    -------
    int
        Return 0 if the command is found else 1
    """
    msg: str
    ret_code: int = 0
    command_info = find_spec(command)

    if command_info:
        msg = _get_command_found_msg(command_info)
    else:
        msg = _get_command_not_found_msg(command)
        ret_code = 1

    sys.stdout.write(msg)
    return ret_code


def _get_command_found_msg(command_info: ModuleSpec) -> str:
    """Return the message to be displayed when the command is found by nbqa.

    Parameters
    ----------
    command_info : ModuleSpec
        Information on the command

    Returns
    -------
    str
        Message to print to stdout.
    """
    command_loc: str = ""
    if command_info.origin:
        command_loc = str(Path(command_info.origin).parent)
    return _COMMAND_FOUND_TEMPLATE.format(
        command=command_info.name, command_loc=command_loc
    )


def _get_command_not_found_msg(command: str) -> str:
    """Return the message to display when the command is not found by nbqa.

    Parameters
    ----------
    command : str
        Command passed to nbqa to find.

    Returns
    -------
    str
        Message to display to stdout.
    """
    python_executable = sys.executable
    nbqa_loc = str(Path(sys.modules["nbqa"].__file__).parent)

    return _COMMAND_NOT_FOUND_TEMPLATE.format(
        command=command, python=python_executable, nbqa_loc=nbqa_loc
    )
