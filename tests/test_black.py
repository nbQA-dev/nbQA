import difflib
import shutil
from pathlib import Path

from nbqa.__main__ import main


def test_black_works(tmpdir):
    shutil.copy(
        str(Path("tests/data") / "test_notebook.ipynb"),
        str(Path(tmpdir) / "test_notebook.ipynb"),
    )
    with open(Path("tests/data") / "test_notebook.ipynb", "r") as handle:
        before = handle.readlines()
    main("black")
    with open(Path("tests/data") / "test_notebook.ipynb", "r") as handle:
        after = handle.readlines()

    result = "".join(difflib.unified_diff(before, after))

    expected = (
        "--- \n"
        "+++ \n"
        "@@ -48,7 +48,7 @@\n"
        '     "%%time\\n",\n'
        '     "def hello(name: str = \\"world\\"):\\n",\n'
        '     "\\n",\n-    "    return f\'hello {name}\'\\n",\n'
        '+    "    return f\\"hello {name}\\"\\n",\n     "\\n",\n'
        '     "\\n",\n     "hello(3)"\n'
    )
    (Path("tests/data") / "test_notebook.ipynb").unlink()

    shutil.copy(
        str(Path(tmpdir) / "test_notebook.ipynb"),
        str(Path("tests/data") / "test_notebook.ipynb"),
    )
    assert result == expected
