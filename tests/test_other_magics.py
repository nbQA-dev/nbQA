"""Check user can check for other magics."""
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, List

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


@pytest.mark.parametrize(
    "magic, expected",
    [
        (
            "--nbqa-ignore-cells=%%custommagic",
            [
                "cell_2:3:1: E402 module level import not at top of file",
                "cell_2:3:1: F401 'glob' imported but unused",
            ],
        ),
        ("--nbqa-ignore-cells=%%custommagic,%%anothercustommagic", []),
    ],
)
def test_cli(magic: str, expected: List[str], capsys: "CaptureFixture") -> None:
    """Check that we can ignore extra cell magics via the CLI."""
    path = Path("tests") / "data/notebook_with_other_magics.ipynb"

    with pytest.raises(SystemExit):
        main(["flake8", str(path), magic])

    out, _ = capsys.readouterr()
    expected_out = "".join(f"{str(path.resolve())}:{i}{os.linesep}" for i in expected)
    assert out == expected_out


@pytest.mark.parametrize(
    "magic, expected",
    [
        (
            "ignore_cells=%%%%custommagic",
            [
                "cell_2:3:1: E402 module level import not at top of file",
                "cell_2:3:1: F401 'glob' imported but unused",
            ],
        ),
        ("ignore_cells=%%%%custommagic,%%%%anothercustommagic", []),
        ("ignore_cells=%%%%custommagic, %%%%anothercustommagic", []),
    ],
)
def test_ini(magic: str, expected: str, capsys: "CaptureFixture") -> None:
    """Check that we can ignore extra cell magics via the config file."""
    path = Path("tests") / "data/notebook_with_other_magics.ipynb"

    with open(".nbqa.ini", "w") as handle:
        handle.write(
            dedent(
                f"""\
                [flake8]
                {magic}
                """
            )
        )

    with pytest.raises(SystemExit):
        main(["flake8", str(path)])

    Path(".nbqa.ini").unlink()

    out, _ = capsys.readouterr()
    expected_out = "".join(f"{str(path.resolve())}:{i}{os.linesep}" for i in expected)
    assert out == expected_out
