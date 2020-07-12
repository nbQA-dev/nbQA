import difflib

from nbqa.__main__ import main


def test_black_works(tmp_notebook_for_testing, capsys):
    """
    Check black works. Should only reformat code cells.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    main("black")
    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = (
        "--- \n"
        "+++ \n"
        "@@ -48,7 +48,7 @@\n"
        '     "%%time\\n",\n'
        '     "def hello(name: str = \\"world\\\\n\\"):\\n",\n'
        '     "\\n",\n-    "    return f\'hello {name}\'\\n",\n'
        '+    "    return f\\"hello {name}\\"\\n",\n     "\\n",\n'
        '     "\\n",\n     "hello(3)"\n'
    )
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
