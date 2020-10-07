"""Detect Ipython magics and provide python code replacements for those magics."""
from typing import Callable, Mapping

# Magic replacement templates
_DEFAULT_TEMPLATE: str = 'type(""" {magic} """)  # {token}'

# We use a comment for replacing cell magic, since we don't want
# cell magic statements to be formatted
# For instance a cell magic placed above a function will be
# formatted to be separated by two blank lines from the function
# It would look odd to have a cell magic followed by blank lines.
_CELL_MAGIC_TEMPLATE: str = "# CELL_MAGIC {magic} {token}"


def is_ipython_magic(source: str) -> bool:
    return source.startswith(("!", "%", "?")) or source.endswith("?")


def _get_default_replacement(token: str, magic: str) -> str:
    return _DEFAULT_TEMPLATE.format(magic=magic, token=token)


def _get_cell_or_line_magic_replacement(token: str, magic: str) -> str:
    if magic.startswith("%%"):
        return _get_cell_magic_replacement(token, magic)

    return _get_default_replacement(token, magic)


def _get_cell_magic_replacement(token: str, magic: str) -> str:
    return _CELL_MAGIC_TEMPLATE.format(magic=magic, token=token)


_MAGIC_HANDLERS: Mapping[str, Callable[..., str]] = {
    "!": _get_default_replacement,
    "?": _get_default_replacement,
    "%": _get_cell_or_line_magic_replacement,
}


def get_magic_replacement(ipython_magic: str, token: str) -> str:
    replacement_line: str = _MAGIC_HANDLERS.get(
        ipython_magic[0],
        # This is to handle magic like str.split??
        _MAGIC_HANDLERS.get(ipython_magic[-1], _get_default_replacement),
    )(token, ipython_magic)

    return replacement_line
