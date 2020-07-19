import pytest

from nbqa.__main__ import main


def test_missing_root_dir(capsys):
    msg = (
        "Please specify both a command and a notebook/directory, e.g.\n"
        "nbqa flake8 my_notebook.ipynb"
    )
    with pytest.raises(ValueError, match=msg):
        main(["flake8", "--ignore=E203"])
