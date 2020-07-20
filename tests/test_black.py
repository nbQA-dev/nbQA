import difflib
import os
import re

import pytest

from nbqa.__main__ import main


def _de_emojify(text):
    # https://stackoverflow.com/a/49986645
    regrex_pattern = re.compile(
        pattern="["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return regrex_pattern.sub(r"", text)


def test_black_works(tmp_notebook_for_testing, capsys):
    """
    Check black works. Should only reformat code cells.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
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
    expected_out = ""
    expected_err = f"reformatted {path}{os.linesep}All done!   {os.linesep}1 file reformatted.{os.linesep}"  # noqa
    assert out == expected_out
    for i in (0, 2):  # haven't figured out how to test the emojis part
        assert err.splitlines()[i] == expected_err.splitlines()[i]
