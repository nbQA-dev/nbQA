"""Check the handling of line magics with and without indentation."""
import json
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_indented_magics(
    tmp_notebook_with_indented_magics: Path,
    capsys: "CaptureFixture",
) -> None:
    """Check if the indented line magics are retained properly after mutating."""
    expected_cell_source = [
        ["import time\n", "\n", 'print(f"current_time: {time.time()}")'],
        [
            "from random import randint\n",
            "\n",
            "if randint(5, 10) > 8:\n",
            '    %time print("Hello world")',
        ],
        ["str.split??"],
        ["# indented line magic\n", "?str.splitlines"],
        ["%time randint(5, 10)"],
    ]
    path = os.path.abspath(str(tmp_notebook_with_indented_magics))

    with open("setup.cfg", "w") as handle:
        handle.write(
            dedent(
                """\
            [nbqa.mutate]
            black=1
            """
            )
        )
    with pytest.raises(SystemExit):
        main(["black", path])

    Path("setup.cfg").unlink()

    with open(tmp_notebook_with_indented_magics) as handle:
        actual_cells = json.load(handle)["cells"]
        actual_cell_source = (cell["source"] for cell in actual_cells)

    for actual, expected in zip(actual_cell_source, expected_cell_source):
        assert actual == expected

    out, _ = capsys.readouterr()
    assert out == ""
