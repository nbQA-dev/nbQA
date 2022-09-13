"""Test files saved via jupytext."""
import os
from pathlib import Path
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_myst(tmp_test_data: Path) -> None:
    """
    Test notebook in myst format.

    Parameters
    ----------
    tmp_test_data
        Temporary copy of test data.
    """
    notebook = tmp_test_data / "notebook_for_testing.md"

    main(["black", str(notebook)])

    with open(notebook, encoding="utf-8") as fd:
        result = fd.read()
    expected = (
        "---\n"
        "jupytext:\n"
        "  text_representation:\n"
        "    extension: .md\n"
        "    format_name: myst\n"
        "    format_version: 0.13\n"
        "    jupytext_version: 1.14.1\n"
        "kernelspec:\n"
        "  display_name: Python 3\n"
        "  language: python\n"
        "  name: python3\n"
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
        "      jupytext_version: 1.14.1\n"
        "  kernelspec:\n    display_name: Python 3\n"
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
        'def hello(name: str = "world\\n"):\n'
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


def test_non_jupytext_md() -> None:
    """Check non-Python markdown will be ignored."""
    ret = main(["black", "README.md"])
    assert ret == 0
    ret = main(["black", os.path.join("docs", "readme.md"), "--nbqa-md"])
    assert ret == 0


def test_jupytext_cant_parse() -> None:
    """Check file jupytext can't parse"""
    ret = main(["black", os.path.join("tests", "invalid_data", "tracker.md")])
    assert ret == 0


def test_jupytext_with_nbqa_md(capsys: "CaptureFixture") -> None:
    """Should work the same whether running on .md or .ipynb file"""
    main(
        [
            "blacken-docs",
            os.path.join("tests", "data", "notebook_for_testing.md"),
            "--nbqa-md",
            "--nbqa-diff",
        ]
    )
    out, _ = capsys.readouterr()
    expected = (
        "\x1b[1mCell 3\x1b[0m\n"
        "------\n"
        "\x1b[1;37m--- tests/data/notebook_for_testing.md\n"
        "\x1b[0m\x1b[1;37m+++ tests/data/notebook_for_testing.md\n"
        "\x1b[0m\x1b[36m@@ -1,3 +1,3 @@\n"
        "\x1b[0m\x1b[31m-2 +2\n"
        "\x1b[0m\x1b[32m+2 + 2\n"
        "\x1b[0m\n"
        "tests/data/notebook_for_testing.md: Rewriting...\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected

    main(
        [
            "blacken-docs",
            os.path.join("tests", "data", "notebook_for_testing.ipynb"),
            "--nbqa-md",
            "--nbqa-diff",
        ]
    )
    out, _ = capsys.readouterr()
    assert out == expected.replace(".md", ".ipynb")
