"""Check what happens when running on non-existent file/directory."""

import pytest

from nbqa.__main__ import main


def test_file_not_found(capsys) -> None:
    """Check useful error message is raised if file or directory doesn't exist."""
    msg = "No such file or directory: I don't exist"

    with pytest.raises(SystemExit):
        main(["isort", "I don't exist", "--profile=black", "--nbqa-mutate"])
    out, err = capsys.readouterr()
    assert msg in out
