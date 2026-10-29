"""Keep the original notebook intact until its replacement is ready."""

import json
import os
import shutil
import stat
from pathlib import Path
from typing import Any

import pytest

from nbqa import replace_source
from nbqa.__main__ import main


@pytest.mark.parametrize(
    "filename", ["notebook_for_testing.ipynb", "notebook_for_testing_copy.md"]
)
@pytest.mark.parametrize("error", [OSError, KeyboardInterrupt])
def test_partial_write_preserves_original(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, filename: str, error: type
) -> None:
    """A failed or interrupted write must not truncate either notebook format."""
    notebook = tmp_path / filename
    shutil.copyfile(Path("tests/data") / filename, notebook)
    original = notebook.read_bytes()

    def interrupted_write(destination: str, *_args: Any, **_kwargs: Any) -> None:
        with open(destination, "w", encoding="utf-8") as handle:
            handle.write("partial notebook")
        raise error("write interrupted")

    monkeypatch.setattr(replace_source, "_write_notebook", interrupted_write)
    if error is OSError:
        assert main(["black", str(notebook)]) == 123
    else:
        with pytest.raises(KeyboardInterrupt):
            main(["black", str(notebook)])

    assert notebook.read_bytes() == original
    assert not list(notebook.parent.glob(".nbqa-*"))


def test_failed_publication_preserves_original(
    tmp_test_data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A fully written replacement must not damage the original if rename fails."""
    notebook = tmp_test_data / "notebook_for_testing.ipynb"
    original = notebook.read_bytes()

    def failed_replace(_source: str, _destination: str) -> None:
        raise OSError("cannot publish notebook")

    monkeypatch.setattr(os, "replace", failed_replace)
    assert main(["black", str(notebook)]) == 123
    assert notebook.read_bytes() == original
    assert not list(notebook.parent.glob(".nbqa-*"))


@pytest.mark.skipif(os.name == "nt", reason="Windows does not preserve POSIX mode bits")
def test_successful_publication_preserves_mode(tmp_test_data: Path) -> None:
    """Replacing a notebook must preserve its original permission bits."""
    notebook = tmp_test_data / "notebook_for_testing.ipynb"
    notebook.chmod(0o640)
    original = notebook.read_bytes()

    assert main(["black", str(notebook)]) == 0
    assert notebook.read_bytes() != original
    assert stat.S_IMODE(notebook.stat().st_mode) == 0o640
    assert not list(notebook.parent.glob(".nbqa-*"))


@pytest.mark.skipif(
    os.name == "nt", reason="Creating symlinks requires Windows privileges"
)
def test_successful_publication_preserves_symlink(tmp_path: Path) -> None:
    """Formatting through a symlink updates its target and keeps the link."""
    target = tmp_path / "actual.ipynb"
    target.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "id": "one",
                        "metadata": {},
                        "source": ["x=1\n"],
                        "outputs": [],
                        "execution_count": None,
                    }
                ],
                "metadata": {"language_info": {"name": "python"}},
                "nbformat": 4,
                "nbformat_minor": 5,
            }
        ),
        encoding="utf-8",
    )
    link = tmp_path / "alias.ipynb"
    link.symlink_to(target)

    assert main(["black", str(link)]) == 0
    assert link.is_symlink()
    assert json.loads(target.read_text(encoding="utf-8"))["cells"][0]["source"] == [
        "x = 1"
    ]
    assert not list(target.parent.glob(".nbqa-*"))
