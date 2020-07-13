import difflib
import subprocess


def test_flake8_works(tmp_notebook_for_testing):
    """
    Check flake8 works. Shouldn't alter the notebook content.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    output = subprocess.run(
        ["python", "-m", "nbqa", "flake8"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    expected_out = (
        "notebook_for_testing.ipynb:cell_1:1:1: F401 'pandas as pd' imported but unused\n"
        "notebook_for_testing.ipynb:cell_1:3:1: F401 'numpy as np' imported but unused\n"
        "notebook_for_testing.ipynb:cell_1:5:1: F401 'os' imported but unused\n"
        "notebook_for_testing.ipynb:cell_3:2:1: E302 expected 2 blank lines, found 1\n"
    )
    expected_err = ""
    assert output.stdout.decode() == expected_out
    assert output.stderr.decode() == expected_err
