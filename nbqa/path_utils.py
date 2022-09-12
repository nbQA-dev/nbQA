"""Utility functions to deal with paths."""
import json
import os
from pathlib import Path
from typing import Tuple


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


def read_notebook(notebook):
    trailing_newline = True
    _, ext = os.path.splitext(notebook)
    with open(notebook, encoding="utf-8") as handle:
        content = handle.read()
    if ext == ".ipynb":
        trailing_newline = content.endswith("\n")
        return json.loads(content), trailing_newline
    elif ext == ".md":
        try:
            import jupytext
        except ImportError:
            return None, None
        md_content = jupytext.jupytext.read(notebook)

        # get lexer: see https://github.com/mwouts/jupytext/issues/993
        from markdown_it import MarkdownIt  # must be installed if you have jupytext

        parser = (
            MarkdownIt("commonmark")
            # we only need to parse block level components (for efficiency)
            .disable("inline", True)
        )
        parsed = parser.parse(content)
        lexer = None
        for token in parsed:
            if token.type == "fence" and token.info.startswith("{code-cell}"):
                lexer = remove_prefix(
                    parser.parse(content)[4].info, "{code-cell}"
                ).strip()
                md_content["metadata"]["language_info"] = {"pygments_lexer": lexer}
                break

        for cell in md_content["cells"]:
            cell["source"] = cell["source"].splitlines(keepends=True)
        if "format_name" in md_content.get("metadata", {}).get("jupytext", {}).get(
            "text_representation", {}
        ):
            return md_content, True
