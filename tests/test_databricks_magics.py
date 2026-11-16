"""Preserve non-Python language cells in Databricks exports."""

import json
from pathlib import Path
from typing import Any

import pytest

from nbqa.__main__ import main


def _notebook(
    path: Path, source: str, *, databricks: bool = True, as_list: bool = True
) -> dict[str, Any]:
    """Write a mixed-language notebook with synthetic outputs and metadata."""
    metadata = (
        {"application/vnd.databricks.v1+notebook": {"language": "python"}}
        if databricks
        else {"language_info": {"name": "python"}}
    )
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": metadata,
        "cells": [
            {
                "cell_type": "code",
                "source": source.splitlines(keepends=True) if as_list else source,
                "metadata": {"tags": ["foreign-language"]},
                "execution_count": 3,
                "outputs": [
                    {"output_type": "stream", "name": "stdout", "text": "saved"}
                ],
            },
            {
                "cell_type": "code",
                "source": ["result= 1\n"],
                "metadata": {},
                "execution_count": None,
                "outputs": [],
            },
        ],
    }
    path.write_text(json.dumps(notebook), encoding="utf-8")
    return notebook


@pytest.mark.parametrize("command", ["black", "ruff format"])
@pytest.mark.parametrize("as_list", [False, True])
@pytest.mark.parametrize(
    "source",
    [
        "%r\nvalue <- 1+1\n",
        '\n  %scala\nprintln( "hello" )\n',
        "%sql --name selected\nVALUES ( 1 )\n",
    ],
)
def test_formatters_preserve_databricks_languages(
    tmp_path: Path, command: str, as_list: bool, source: str
) -> None:
    """Skip complete foreign cells while still formatting neighboring Python."""
    path = tmp_path / "mixed.ipynb"
    original = _notebook(path, source, as_list=as_list)

    assert main([command, str(path)]) == 0

    updated = json.loads(path.read_text(encoding="utf-8"))
    assert updated["cells"][0] == original["cells"][0]
    assert updated["metadata"] == original["metadata"]
    assert "".join(updated["cells"][1]["source"]) == "result = 1"


@pytest.mark.parametrize(
    "source, rule",
    [
        ("%r\nvalue <- 1 + 1\n", "B015"),
        ('%scala\nprintln("hello")\n', "F821"),
        ("%sql\nVALUES(1)\n", "F821"),
    ],
)
def test_linters_ignore_databricks_languages(
    tmp_path: Path, source: str, rule: str
) -> None:
    """Do not report Python diagnostics on valid foreign-language statements."""
    path = tmp_path / "mixed.ipynb"
    _notebook(path, source)
    original = path.read_bytes()

    assert main(["ruff", str(path), f"--select={rule}"]) == 0
    assert path.read_bytes() == original


def test_python_diagnostics_keep_cell_numbers(tmp_path: Path, capsys: Any) -> None:
    """Skipping a language cell preserves the following Python cell's mapping."""
    path = tmp_path / "mixed.ipynb"
    notebook = _notebook(path, "%r\nvalue <- 1 + 1\n")
    notebook["cells"][1]["source"] = ["missing_name\n"]
    path.write_text(json.dumps(notebook), encoding="utf-8")

    assert main(["ruff", str(path), "--select=F821"]) == 1

    out, _ = capsys.readouterr()
    assert "cell_2:1:1" in out
    assert "missing_name" in out
    assert "cell_1" not in out


def test_process_cells_override(tmp_path: Path) -> None:
    """Honor an explicit opt-in for a language-named custom magic."""
    path = tmp_path / "mixed.ipynb"
    _notebook(path, "%r\nvalue=1\n")

    assert main(["black", str(path), "--nbqa-process-cells= r "]) == 0

    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert "".join(notebook["cells"][0]["source"]) == "%r\nvalue = 1"


@pytest.mark.parametrize("header", ["%python", "%matplotlib inline", "%r_custom"])
def test_databricks_python_and_line_magics(tmp_path: Path, header: str) -> None:
    """Keep processing Python and other line magics in Databricks notebooks."""
    path = tmp_path / "mixed.ipynb"
    _notebook(path, f"{header}\nvalue=1\n")

    assert main(["black", str(path)]) == 0

    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert "".join(notebook["cells"][0]["source"]) == f"{header}\nvalue = 1"


@pytest.mark.parametrize("header", ["%r", "%scala", "%sql SELECT 1"])
def test_jupyter_line_magics(tmp_path: Path, header: str) -> None:
    """Do not infer Databricks cell semantics in ordinary Jupyter notebooks."""
    path = tmp_path / "mixed.ipynb"
    _notebook(path, f"{header}\nvalue=1\n", databricks=False)

    assert main(["black", str(path)]) == 0

    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert "".join(notebook["cells"][0]["source"]) == f"{header}\nvalue = 1"
