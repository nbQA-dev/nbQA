import difflib
import json
import shutil
from pathlib import Path

from nbqa.__main__ import main


def test_black_works(tmpdir):
    shutil.copy(
        str(Path("tests/data") / "test_notebook.ipynb"),
        str(Path(tmpdir) / "test_notebook.ipynb"),
    )
    with open(Path("tests/data") / "test_notebook.ipynb", "r") as handle:
        before = json.loads(handle.read())
    main("black")
    with open(Path("tests/data") / "test_notebook.ipynb", "r") as handle:
        after = json.loads(handle.read())

    # check non-cells haven't changed:
    for i in ["metadata", "nbformat", "nbformat_minor"]:
        assert before[i] == after[i]

    before_sources = ["".join(i["source"]) for i in before["cells"]]
    after_sources = ["".join(i["source"]) for i in after["cells"]]

    result = [
        "".join(difflib.unified_diff(bef, aft))
        for bef, aft in zip(before_sources, after_sources)
    ]
    expected = [
        "",
        "--- \n+++ \n@@ -50,7 +50,7 @@\n n   f-'+\" h e l@@ -63,7 +63,7 @@\n m e }-'+\" \n \n \n",
        "",
    ]

    (Path("tests/data") / "test_notebook.ipynb").unlink()

    shutil.copy(
        str(Path(tmpdir) / "test_notebook.ipynb"),
        str(Path("tests/data") / "test_notebook.ipynb"),
    )

    assert result == expected
