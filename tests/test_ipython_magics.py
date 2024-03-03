"""Check user can check for other magics."""

import difflib
import os
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Callable, Sequence

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from py._path.local import LocalPath


def _create_ignore_cell_config(config_file_path: Path, config: str) -> None:
    """Create configuration file for nbqa."""
    config_file_path.write_text(config)


def _copy_notebook(src_nb: Path, target_dir: Path) -> Path:
    """Copy source notebook to the target directory."""
    test_nb_path = target_dir / src_nb.name
    copyfile(src_nb, test_nb_path)
    return test_nb_path


def _validate_magics_with_black(before: Sequence[str], after: Sequence[str]) -> bool:
    """
    Validate the state of the notebook before and after running nbqa with black.

    Parameters
    ----------
    before
        Notebook contents before running nbqa with black
    after
        Notebook contents after running nbqa with black

    Returns
    -------
    bool
        True if validation succeeded else False
    """
    diff = difflib.unified_diff(before, after)
    result = "".join(i for i in diff if any([i.startswith("+ "), i.startswith("- ")]))
    expected = (
        '-    "def compute(operand1,operand2, bin_op):\\n",\n'
        '+    "def compute(operand1, operand2, bin_op):\\n",\n'
        '-    "compute(5,1, operator.add)"\n'
        '+    "compute(5, 1, operator.add)"\n'
        '-    "    ?str.splitlines"\n'
        '+    "str.splitlines?"\n'
        '-    "   %time randint(5,10)"\n'
        '+    "%time randint(5,10)"\n'
        '-    "result = str.split??"\n'
        '+    "str.split??"\n'
    )
    return result == expected


def test_indented_magics(
    tmp_notebook_with_indented_magics: "LocalPath",
) -> None:
    """Check if the indented line magics are retained properly after mutating."""
    with open(str(tmp_notebook_with_indented_magics), encoding="utf-8") as handle:
        before = handle.readlines()
    main(
        ["black", os.path.join("tests", "data", "notebook_with_indented_magics.ipynb")]
    )
    with open(str(tmp_notebook_with_indented_magics), encoding="utf-8") as handle:
        after = handle.readlines()

    assert _validate_magics_with_black(before, after)


def _validate_magics_flake8_warnings(actual: str, test_nb_path: Path) -> bool:
    """Validate the results of notebooks with warnings."""
    expected = (
        f"{str(test_nb_path)}:cell_1:1:1: F401 'random.randint' imported but unused\n"
        f"{str(test_nb_path)}:cell_1:2:1: F401 'IPython.get_ipython' imported but unused\n"
        f"{str(test_nb_path)}:cell_3:6:21: E231 missing whitespace after ','\n"
        f"{str(test_nb_path)}:cell_3:11:10: E231 missing whitespace after ','\n"
    )
    return actual == expected


@pytest.mark.parametrize(
    "config, validate",
    [
        (
            "--extend-ignore=F821",
            _validate_magics_flake8_warnings,
        ),
    ],
)
def test_magics_with_flake8(
    config: str,
    validate: Callable[..., bool],
    tmpdir: "LocalPath",
    capsys: "CaptureFixture",
) -> None:
    """Test nbqa with flake8 on notebook with different types of ipython magics."""
    test_nb_path = _copy_notebook(
        Path("tests/data/notebook_with_indented_magics.ipynb"), Path(tmpdir)
    )

    main(["flake8", str(test_nb_path), config])

    out, _ = capsys.readouterr()
    assert validate(out, test_nb_path)
