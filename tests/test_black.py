import difflib
import os

import pytest

from nbqa.__main__ import main


def test_black_works(tmp_notebook_for_testing, capsys):
    """
    Check black works. Should only reformat code cells.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    with pytest.raises(SystemExit):
        main(["black", path])
    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = (
        "-    \"    return f'hello {name}'\\n\",\n"
        '+    "    return f\\"hello {name}\\"\\n",\n'
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = []
    expected_err = [
        f"reformatted {path}",
        "All done! \u2728 \U0001f370 \u2728",
        "1 file reformatted.",
    ]  # noqa
    assert out.splitlines() == expected_out
    assert err.splitlines() == expected_err
