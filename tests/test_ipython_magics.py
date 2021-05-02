"""Check user can check for other magics."""
import difflib
from pathlib import Path
from shutil import copyfile
from textwrap import dedent
from typing import TYPE_CHECKING, Callable, Optional, Sequence

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
    result = "".join([i for i in diff if any([i.startswith("+ "), i.startswith("- ")])])
    expected = dedent(
        """\
        -    "def compute(operand1,operand2, bin_op):\\n",
        +    "def compute(operand1, operand2, bin_op):\\n",
        -    "compute(5,1, operator.add)"
        +    "compute(5, 1, operator.add)"
        -    "    ?str.splitlines"
        +    "?str.splitlines"
        -    "    !grep -r '%%HTML' . | wc -l"
        +    "!grep -r '%%HTML' . | wc -l"
        -    "   %time randint(5,10)"
        +    "%time randint(5, 10)"
        -    "    %time compute(5,1, operator.mul)"
        +    "    %time compute(5, 1, operator.mul)"
        -    "!pip list 2>&1 |\\\\"
        +    "!pip list 2>&1 |"
        """
    )
    return result == expected


@pytest.mark.parametrize(
    "config, validate, config_file",
    [
        (
            "[tool.nbqa.mutate]\nblack=1",
            _validate_magics_with_black,
            "pyproject.toml",
        )
    ],
)
def test_indented_magics(
    config: str,
    validate: Callable[..., bool],
    config_file: Optional[str],
    tmpdir: "LocalPath",
) -> None:
    """Check if the indented line magics are retained properly after mutating."""
    test_nb_path = _copy_notebook(
        Path("tests/data/notebook_with_indented_magics.ipynb"), Path(tmpdir)
    )

    if config_file:
        _create_ignore_cell_config(Path(tmpdir) / config_file, config)

    with open(str(test_nb_path)) as handle:
        before = handle.readlines()

    main(["black", str(test_nb_path)])

    with open(str(test_nb_path)) as handle:
        after = handle.readlines()

    assert validate(before, after)


def _validate_magics_flake8_warnings(actual: str, test_nb_path: Path) -> bool:
    """Validate the results of notebooks with warnings."""
    expected_out = [
        f"{str(test_nb_path)}:cell_3:6:21: E231 missing whitespace after ','",
        f"{str(test_nb_path)}:cell_3:11:10: E231 missing whitespace after ','",
        f"{str(test_nb_path)}:cell_9:1:14: E231 missing whitespace after ','",
        f"{str(test_nb_path)}:cell_10:2:18: E231 missing whitespace after ','",
        f"{str(test_nb_path)}:cell_12:1:1: E402 module level import not at top of file",
        f"{str(test_nb_path)}:cell_12:2:1: E402 module level import not at top of file",
    ]
    return sorted(expected_out) == sorted(actual.splitlines())


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
