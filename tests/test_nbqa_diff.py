"""Check --nbqa-diff flag."""

import re
from pathlib import Path

import pytest

from nbqa.__main__ import main

TESTS_DIR = Path("tests")
TEST_DATA_DIR = TESTS_DIR / "data"

DIRTY_NOTEBOOK = TEST_DATA_DIR / "notebook_for_testing.ipynb"
CLEAN_NOTEBOOK = TEST_DATA_DIR / "clean_notebook.ipynb"


def test_diff_present(capsys):
    with pytest.raises(SystemExit):
        main(["black", str(DIRTY_NOTEBOOK), "--nbqa-diff"])
    out, err = capsys.readouterr()
    expected_out = """\
\x1b[1mCell 2\x1b[0m
------
--- tests/data/notebook_for_testing.ipynb
+++ tests/data/notebook_for_testing.ipynb
@@ -12,8 +12,8 @@
     'hello goodbye'
     \"\"\"

\x1b[31m-    return 'hello {}'.format(name)
\x1b[0m\x1b[32m+    return "hello {}".format(name)
\x1b[0m

 !ls
\x1b[31m-hello(3)
\x1b[0m\x1b[32m+hello(3)
\x1b[0m
\x1b[1mCell 4\x1b[0m
------
--- tests/data/notebook_for_testing.ipynb
+++ tests/data/notebook_for_testing.ipynb
@@ -1,4 +1,4 @@
 from random import randint

 if __debug__:
\x1b[31m-    %time randint(5,10)
\x1b[0m\x1b[32m+    %time randint(5, 10)
\x1b[0m
To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`
"""
    assert out == expected_out
    assert err == ""


def test_diff_and_mutate():
    """
    Check a ValueError is raised if we use both --nbqa-mutate and --nbqa-diff.
    """
    msg = re.escape(
        """\
Cannot use both `--nbqa-diff` and `--nbqa-mutate` flags together!

Use `--nbqa-diff` to preview changes, and `--nbqa-mutate` to apply them.\
"""
    )
    with pytest.raises(ValueError, match=msg):
        main(["black", str(DIRTY_NOTEBOOK), "--nbqa-mutate", "--nbqa-diff"])
