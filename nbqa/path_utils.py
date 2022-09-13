"""Utility functions to deal with paths."""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def remove_prefix(string: str, prefix: str) -> str:
    """
    Remove prefix from string.

    Parameters
    ----------
    string
        Given string to remove prefix from.
    prefix
        Prefix to remove.

    Raises
    ------
    AssertionError
        If string doesn't start with given prefix.
    """
    if string.startswith(prefix):
        string = string[len(prefix) :]
    else:  # pragma: nocover
        raise AssertionError(f"{string} doesn't start with prefix {prefix}")
    return string


def remove_suffix(string: str, suffix: str) -> str:
    """
    Remove suffix from string.

    Parameters
    ----------
    string
        Given string to remove suffix from.
    suffix
        Suffix to remove.

    Raises
    ------
    AssertionError
        If string doesn't end with given suffix.
    """
    if string.endswith(suffix):
        string = string[: -len(suffix)]
    else:  # pragma: nocover
        raise AssertionError(f"{string} doesn't end with suffix {suffix}")
    return string


def get_relative_and_absolute_paths(path: str) -> Tuple[str, str]:
    """Get relative (if possible) and absolute versions of path."""
    absolute_path = Path(path).resolve()
    try:
        relative_path = absolute_path.relative_to(Path.cwd())
    except ValueError:
        relative_path = absolute_path
    return str(relative_path), str(absolute_path)


def read_notebook(notebook: str) -> Tuple[Optional[Dict[str, Any]], Optional[bool]]:
    """
    Read notebook.

    If it's .md, try reading it with jupytext. If can't, ignore it.

    Parameters
    ----------
    notebook
        Path of notebook.

    Returns
    -------
    notebook_json
        Parsed notebook
    trailing_newline
        Whether the notebook originally had a trailing newline
    """
    trailing_newline = True
    _, ext = os.path.splitext(notebook)
    with open(notebook, encoding="utf-8") as handle:
        content = handle.read()
    if ext == ".ipynb":
        trailing_newline = content.endswith("\n")
        return json.loads(content), trailing_newline
    assert ext == ".md"
    try:
        import jupytext  # pylint: disable=import-outside-toplevel
        from markdown_it import MarkdownIt  # pylint: disable=import-outside-toplevel
    except ImportError:  # pragma: nocover (how to test this?)
        return None, None
    md_content = jupytext.jupytext.read(notebook)

    if (
        md_content.get("metadata", {}).get("kernelspec", {}).get("language", {})
        != "python"
    ):
        return None, None

    # get lexer: see https://github.com/mwouts/jupytext/issues/993
    parser = MarkdownIt("commonmark").disable("inline", True)
    parsed = parser.parse(content)
    lexer = None
    for token in parsed:
        if token.type == "fence" and token.info.startswith("{code-cell}"):
            lexer = remove_prefix(token.info, "{code-cell}").strip()
            md_content["metadata"]["language_info"] = {"pygments_lexer": lexer}
            break

    for cell in md_content["cells"]:
        cell["source"] = cell["source"].splitlines(keepends=True)
    if "format_name" in md_content.get("metadata", {}).get("jupytext", {}).get(
        "text_representation", {}
    ):
        return md_content, True
    return None, None  # how to cover this?
