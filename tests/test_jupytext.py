"""Test files saved via jupytext."""
import os
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from py._path.local import LocalPath


def test_non_jupytext_md() -> None:
    """Check non-Python markdown will be ignored."""
    ret = main(["black", "README.md"])
    assert ret == 0
    ret = main(["black", os.path.join("docs", "readme.md"), "--nbqa-md"])
    assert ret == 0


def test_invalid_config_file(tmpdir: "LocalPath") -> None:
    """If reading config file fails, don't fail whole process."""
    config_file = (
        "Type: Jupyter Notebook Extension\n"
        "Name: Jupytext\n"
        "Section: notebook\n"
        "Description: Jupytext Menu\n"
        "tags:\n"
        "- version control\n"
        "- markdown\n"
        "- script\n"
        "Link: README.md\n"
        "Icon: jupytext_menu_zoom.png\n"
        "Main: index.js\n"
        "Compatibility: 5.x, 6.x\n"
    )
    with open(os.path.join(tmpdir, "jupytext.yml"), "w", encoding="utf-8") as fd:
        fd.write(config_file)

    with open(os.path.join(tmpdir, "foo.md"), "w", encoding="utf-8") as fd:
        fd.write("bar\n")

    with pytest.warns(
        DeprecationWarning,
        match=r"Passing unrecognized arguments to super\(JupytextConfiguration\)",
    ):
        main(["black", os.path.join(tmpdir, "foo.md")])
