import pytest

from nbqa.__main__ import main


def test_missing_command():
    command = "some-fictional-command"
    msg = (
        f"Command `{command}` not found. "
        "Please make sure you have it installed before running nbQA on it."
    )
    with pytest.raises(ValueError, match=msg):
        main([command, "--some-flag"])
