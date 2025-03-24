"""Test files saved via jupytext."""

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import jupytext

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from py._path.local import LocalPath


def test_myst(tmp_test_data: Path) -> None:
    """
    Test notebook in myst format.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    notebook = tmp_test_data / "notebook_for_testing.md"

    with open(tmp_test_data / ".jupytext.toml", "w", encoding="utf-8") as fd:
        fd.write('notebook_metadata_filter = "substitutions"\n')
    main(["black", str(notebook)])
    os.remove(tmp_test_data / ".jupytext.toml")

    with open(notebook, encoding="utf-8") as fd:
        result = fd.read()
    expected = (
        "---\n"
        "jupytext:\n"
        "  text_representation:\n"
        "    extension: .md\n"
        "    format_name: myst\n"
        "    format_version: 0.13\n"
        f"    jupytext_version: {jupytext.__version__}\n"
        "kernelspec:\n"
        "  display_name: Python 3\n"
        "  language: python\n"
        "  name: python3\n"
        "substitutions:\n"
        "  extra_dependencies: bokeh\n"
        "---\n"
        "\n"
        "```{code-cell} ipython3\n"
        ":tags: [skip-flake8]\n"
        "\n"
        "import os\n"
        "\n"
        "import glob\n"
        "\n"
        "import nbqa\n"
        "```\n"
        "\n"
        "# Some markdown cell containing \\\\n"
        "\n"
        "\n"
        '+++ {"tags": ["skip-mdformat"]}\n'
        "\n"
        "# First level heading\n"
        "\n"
        "```{code-cell} ipython3\n"
        ":tags: [flake8-skip]\n"
        "\n"
        "%%time foo\n"
        'def hello(name: str = "world\\n'
        '"):\n'
        '    """\n'
        "    Greet user.\n"
        "\n"
        "    Examples\n"
        "    --------\n"
        "    >>> hello()\n"
        "    'hello world\\\\n"
        "'\n"
        "\n"
        '    >>> hello("goodbye")\n'
        "    'hello goodbye'\n"
        '    """\n'
        "\n"
        '    return "hello {}".format(name)\n'
        "\n"
        "\n"
        "!ls\n"
        "hello(3)\n"
        "```\n"
        "\n"
        "```python\n"
        "2 +2\n"
        "```\n"
        "\n"
        "```{code-cell} ipython3\n"
        "    %%bash\n"
        "\n"
        "        pwd\n"
        "```\n"
        "\n"
        "```{code-cell} ipython3\n"
        "from random import randint\n"
        "\n"
        "if __debug__:\n"
        "    %time randint(5,10)\n"
        "```\n"
        "\n"
        "```{code-cell} ipython3\n"
        "import pprint\n"
        "import sys\n"
        "\n"
        "if __debug__:\n"
        "    pretty_print_object = pprint.PrettyPrinter(\n"
        "        indent=4, width=80, stream=sys.stdout, compact=True, depth=5\n"
        "    )\n"
        "\n"
        'pretty_print_object.isreadable(["Hello", "World"])\n'
        "```\n"
    )
    assert result == expected


def test_md(tmp_test_data: Path) -> None:
    """
    Notebook in md format.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    notebook = tmp_test_data / "notebook_for_testing_copy.md"

    main(["black", str(notebook)])

    with open(notebook, encoding="utf-8") as fd:
        result = fd.read()
    expected = (
        "---\n"
        "jupyter:\n"
        "  jupytext:\n"
        "    text_representation:\n"
        "      extension: .md\n"
        "      format_name: markdown\n"
        "      format_version: '1.3'\n"
        f"      jupytext_version: {jupytext.__version__}\n"
        "  kernelspec:\n"
        "    display_name: Python 3\n"
        "    language: python\n"
        "    name: python3\n"
        "---\n"
        "\n"
        "```python\n"
        "import os\n"
        "\n"
        "import glob\n"
        "\n"
        "import nbqa\n"
        "```\n"
        "\n"
        "# Some markdown cell containing \\n"
        "\n"
        "\n"
        "```python\n"
        "%%time\n"
        'def hello(name: str = "world\\n'
        '"):\n'
        '    """\n'
        "    Greet user.\n"
        "\n"
        "    Examples\n"
        "    --------\n"
        "    >>> hello()\n"
        "    'hello world\\\\n"
        "'\n"
        '    >>> hello("goodbye")\n'
        "    'hello goodby'\n"
        '    """\n'
        "    if True:\n"
        "        %time # indented magic!\n"
        '    return f"hello {name}"\n'
        "\n"
        "\n"
        "hello(3)\n"
        "```\n"
        "\n"
        "```python\n"
        "\n"
        "```\n"
    )
    assert result == expected


def test_qmd(tmp_test_data: Path) -> None:
    """
    Notebook in qmd format.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    notebook = tmp_test_data / "notebook_for_testing.qmd"

    main(["black", str(notebook)])

    with open(notebook, encoding="utf-8") as fd:
        result = fd.read()
    expected = (
        """---\n"""
        """title: Quarto Basics\n"""
        """format:\n"""
        """  html:\n"""
        """    code-fold: true\n"""
        """jupyter:\n"""
        """  jupytext:\n"""
        """    text_representation:\n"""
        """      extension: .qmd\n"""
        """      format_name: quarto\n"""
        """      format_version: '1.0'\n"""
        """      jupytext_version: 1.16.7\n"""
        """  kernelspec:\n"""
        """    display_name: Python 3\n"""
        """    language: python\n"""
        """    name: python3\n"""
        """---\n"""
        """\n"""
        """```{python}\n"""
        """#| label: fig-polar\n"""
        """#| fig-cap: |-\n"""
        """#|   A line plot on a polar axis\n"""
        """#|   Additional content\n"""
        """# This is a comment that stops cell options\n"""
        """# | fig-subcap: A line plot on a polar axis\n"""
        """# |  Additional content\n"""
        """\n"""
        """import numpy as np\n"""
        """import matplotlib.pyplot as plt\n"""
        """\n"""
        """r = np.arange(0, 2, 0.01)\n"""
        """theta = 2 * np.pi * r\n"""
        """fig, ax = plt.subplots(subplot_kw={"projection": "polar"})\n"""
        """ax.plot(theta, r)\n"""
        """ax.set_rticks([0.5, 1, 1.5, 2])\n"""
        """ax.grid(True)\n"""
        """plt.show()\n"""
        """```\n"""
        """\n"""
        """# Other Markdown\n"""
        """This content should not change in any way.\n"""
        """#| cell option like line\n"""
        """#comment like line\n"""
        """code that won't get formatted\n"""
        """ax.set_rticks([0.5,1,1.5,2])\n"""
    )
    assert result == expected


def test_non_jupytext_md() -> None:
    """Check non-Python markdown will be ignored."""
    ret = main(["black", "README.md"])
    assert ret == 0
    ret = main(["black", os.path.join("docs", "readme.md"), "--nbqa-md"])
    assert ret == 0


def test_non_python_md() -> None:
    """Skip non-Python notebooks."""
    ret = main(["black", os.path.join("tests", "invalid_data", "octave_notebook.md")])
    assert ret == 0


def test_jupytext_cant_parse() -> None:
    """Check file jupytext can't parse"""
    ret = main(["black", os.path.join("tests", "invalid_data", "tracker.md")])
    assert ret == 0


def test_jupytext_with_nbqa_md(capsys: "CaptureFixture") -> None:
    """Should work the same whether running on .md or .ipynb file"""
    path = os.path.join("tests", "data", "notebook_for_testing.md")
    main(
        [
            "blacken-docs",
            path,
            "--nbqa-md",
            "--nbqa-diff",
        ]
    )
    out, _ = capsys.readouterr()
    expected = (
        "\x1b[1mCell 3\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1,3 +1,3 @@\n"
        "\x1b[0m\x1b[31m-2 +2\n"
        "\x1b[0m\x1b[32m+2 + 2\n"
        "\x1b[0m\n"
        f"{path}: Rewriting...\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out.replace("\r\n", "\n") == expected

    main(
        [
            "blacken-docs",
            os.path.join("tests", "data", "notebook_for_testing.ipynb"),
            "--nbqa-md",
            "--nbqa-diff",
        ]
    )
    out, _ = capsys.readouterr()
    assert out.replace("\r\n", "\n") == expected.replace(".md", ".ipynb")


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


def test_jupytext_on_folder(capsys: "CaptureFixture") -> None:
    """Check invalid files aren't checked."""
    path = os.path.join("tests", "invalid_data")
    main(
        [
            "pydocstyle",
            path,
        ]
    )
    out, _ = capsys.readouterr()
    expected = (
        f"{os.path.join(path, 'invalid_syntax.ipynb')}:cell_1:0 at module level:\n"
        "        D100: Missing docstring in public module\n"
        f"{os.path.join(path, 'assignment_to_literal.ipynb')}:cell_1:0 at module level:\n"
        "        D100: Missing docstring in public module\n"
        f"{os.path.join(path, 'automagic.ipynb')}:cell_1:0 at module level:\n"
        "        D100: Missing docstring in public module\n"
    )
    assert "\n".join(sorted(out.splitlines())) == "\n".join(
        sorted(expected.splitlines())
    )
