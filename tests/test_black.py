import difflib
import subprocess


def test_black_works(tmp_notebook_for_testing):
    """
    Check black works. Should only reformat code cells.
    """
    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    output = subprocess.run(
        ["python", "-m", "nbqa", "black", "tests/data/notebook_for_testing.ipynb"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
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
    expected_out = ""
    expected_err = (
        "reformatted notebook_for_testing.ipynb\nAll done! ✨ 🍰 ✨\n1 file reformatted.\n"
    )
    assert output.stdout.decode() == expected_out
    assert output.stderr.decode() == expected_err
