"""Utility functions to deal with paths."""
import json
import os
import string
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def remove_prefix(string_: str, prefix: str) -> str:
    """
    Remove prefix from string.

    Parameters
    ----------
    string_
        Given string to remove prefix from.
    prefix
        Prefix to remove.

    Raises
    ------
    AssertionError
        If string doesn't start with given prefix.
    """
    if string_.startswith(prefix):
        string_ = string_[len(prefix) :]
    else:  # pragma: nocover
        raise AssertionError(f"{string_} doesn't start with prefix {prefix}")
    return string_


def remove_suffix(string_: str, suffix: str) -> str:
    """
    Remove suffix from string.

    Parameters
    ----------
    string_
        Given string to remove suffix from.
    suffix
        Suffix to remove.

    Raises
    ------
    AssertionError
        If string doesn't end with given suffix.
    """
    if string_.endswith(suffix):
        string_ = string_[: -len(suffix)]
    else:  # pragma: nocover
        raise AssertionError(f"{string_} doesn't end with suffix {suffix}")
    return string_


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

    from jupytext.config import (  # pylint: disable=import-outside-toplevel
        JupytextConfigurationError,
        load_jupytext_config,
    )

    try:
        config = load_jupytext_config(os.path.abspath(notebook))
    except JupytextConfigurationError:
        config = None

    try:
        md_content = jupytext.jupytext.read(notebook, config=config)
    except:  # noqa: E72a  # pylint: disable=bare-except
        return None, None

    if ("kernelspec" not in md_content.get("metadata", {})) or (
        (
            md_content.get("metadata", {})
            .get("kernelspec", {})
            .get("language", "")
            .rstrip(string.digits)
            != "python"
        )
        and (
            md_content.get("metadata", {})
            .get("kernelspec", {})
            .get("name", "")
            .rstrip(string.digits)
            != "python"
        )
    ):
        # Not saved with jupytext, or not Python
        return None, None

    # get lexer: see https://github.com/mwouts/jupytext/issues/993
    parsed = MarkdownIt("commonmark").disable("inline", True).parse(content)
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
    return None, None  # pragma: nocover (defensive check, shouldn't get here)
