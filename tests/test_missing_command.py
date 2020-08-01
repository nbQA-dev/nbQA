"""
Check useful error message if command isn't valid.

E.g. if you run :code:`nbqa flake .` and don't have :code:`flake8` installed.
"""

import pytest

from nbqa.__main__ import main


def test_missing_command() -> None:
    """Check useful error is raised if :code:`nbqa` is run with an invalid command."""
    command = "some-fictional-command"
    msg = (
        f"Command `{command}` not found. "
        "Please make sure you have it installed before running nbQA on it."
    )
    with pytest.raises(
        ValueError, match=msg,
    ):
        main([command, "tests", "--some-flag"])
