"""Check that users are encouraged to report bugs if reconstructing notebook fails."""

import re
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


@pytest.mark.parametrize(
    ("command", "out_pattern"),
    [
        ("black", r'black is found by nbqa at ".*"\s*!\s*'),
        (
            "some-fictional-command",
            dedent(
                """\
            {command} cannot be found by nbqa.
            Python executable: .*
            nbqa location: .*

            It seems {command} is not installed in the same python environment as nbqa.
            Please run `.* -m pip install {command}` so that nbqa can find {command}.

            To install nbqa in a python virtual environment please refer to
            https://nbqa.readthedocs.io/en/latest/readme.html#installation
            """
            ).format(command="some-fictional-command"),
        ),
    ],
)
def test_nbqa_find_flag(
    command: str, out_pattern: str, capsys: "CaptureFixture"
) -> None:
    """Check the message displayed when :code:`nbqa` is run with --nbqa-find flag."""
    with pytest.raises(SystemExit):
        main([command, "tests", "--nbqa-find"])

    out, _ = capsys.readouterr()
    assert re.fullmatch(out_pattern, out) is not None
