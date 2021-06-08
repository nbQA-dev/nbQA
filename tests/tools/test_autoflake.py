"""Check configs from :code:`pyproject.toml` are picked up."""
import difflib
from pathlib import Path
from shutil import copyfile
from textwrap import dedent
from typing import TYPE_CHECKING, Sequence, Tuple

from nbqa.__main__ import main

if TYPE_CHECKING:
    from py._path.local import LocalPath


def _copy_notebook(src_notebook: Path, target_dir: Path) -> Path:
    """
    Copy source notebook to the target directory.

    Parameters
    ----------
    src_notebook : Path
        Notebook to copy
    target_dir : Path
        Destination directory

    Returns
    -------
    Path
        Path to the notebook in the destination directory
    """
    target_notebook = target_dir / src_notebook.name
    copyfile(src_notebook, target_notebook)
    return target_notebook


def _run_nbqa(
    command: str, notebook: str, *args: str
) -> Tuple[Sequence[str], Sequence[str]]:
    """
    Run nbQA on the given notebook using the input command.

    Parameters
    ----------
    command
        Third party tool to run
    notebook
        Notebook given to nbQA

    Returns
    -------
    Tuple[Sequence[str], Sequence[str]]
        Content of the notebook before and after running nbQA
    """
    with open(notebook) as handle:
        before = handle.readlines()

    main([command, notebook, *args])

    with open(notebook) as handle:
        after = handle.readlines()

    return (before, after)


def _validate(before: Sequence[str], after: Sequence[str]) -> bool:
    """
    Validate the state of the notebook before and after running nbqa with autoflake.

    Parameters
    ----------
    before
        Notebook contents before running nbqa with autoflake
    after
        Notebook contents after running nbqa with autoflake

    Returns
    -------
    bool
        True if validation succeeded else False
    """
    diff = difflib.unified_diff(before, after)
    result = "".join(i for i in diff if any([i.startswith("+ "), i.startswith("- ")]))

    expected = dedent(
        """\
        -    "    unused_var = \\"not used\\"\\n",
        -    "from os.path import *\\n",
        +    "from os.path import abspath\\n",
        -    "import pandas as pd\\n",
        """
    )
    return result == expected


def test_autoflake_cli(tmpdir: "LocalPath") -> None:
    """
    Check if autoflake works as expected using the command line configuration.

    Parameters
    ----------
    tmpdir
        Temporary folder for testing.
    """
    target_notebook = _copy_notebook(
        Path("tests/data/notebook_for_autoflake.ipynb"), Path(tmpdir)
    )

    before, after = _run_nbqa(
        "autoflake",
        str(target_notebook),
        "--in-place",
        "--expand-star-imports",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--nbqa-mutate",
    )

    assert _validate(before, after)


def _create_toml_config(config_file: Path) -> None:
    """
    Create TOML configuration in the test directory.

    Parameters
    ----------
    config_file : Path
        nbqa configuration file
    """
    config_file.write_text(
        dedent(
            """
            [tool.nbqa.mutate]
            autoflake = 1

            [tool.nbqa.addopts]
            autoflake = [
                "--in-place",
                "--expand-star-imports",
                "--remove-all-unused-imports",
                "--remove-unused-variables"
            ]
            """
        )
    )


def test_autoflake_toml(tmpdir: "LocalPath") -> None:
    """
    Check if autoflake works as expected using the configuration from pyproject.toml.

    Parameters
    ----------
    tmpdir
        Temporary folder for testing.
    """
    target_notebook = _copy_notebook(
        Path("tests/data/notebook_for_autoflake.ipynb"), Path(tmpdir)
    )

    _create_toml_config(Path(tmpdir) / "pyproject.toml")

    before, after = _run_nbqa("autoflake", str(target_notebook))

    assert _validate(before, after)
