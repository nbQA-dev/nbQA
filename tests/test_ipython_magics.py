"""Check user can check for other magics."""
import difflib
from pathlib import Path
from shutil import copyfile
from textwrap import dedent
from typing import TYPE_CHECKING, Callable, Optional, Sequence, Tuple

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


def _validate_ignore_cells_with_warning(actual: str, test_nb_path: Path) -> bool:
    """Validate the results of notebooks with warnings."""
    expected_out = [
        "cell_2:3:1: F401 'glob' imported but unused",
    ]
    expected = "".join(f"{str(test_nb_path)}:{i}\n" for i in expected_out)
    return expected == actual


def _validate_ignore_cells_without_warning(actual: str, _: Path) -> bool:
    """Validate the results of notebooks without warnings."""
    expected = ""
    return expected == actual


def _ignore_cells_cli_input() -> Sequence[
    Tuple[str, Callable[..., bool], Optional[str]]
]:
    """Input for ignore cells test case with configuration passed as CLI arguments."""
    return [
        (
            "--nbqa-ignore-cells=%%custommagic",
            _validate_ignore_cells_with_warning,
            None,
        ),
        (
            "--nbqa-ignore-cells=%%custommagic,%%anothercustommagic",
            _validate_ignore_cells_without_warning,
            None,
        ),
    ]


def _ignore_cells_ini_input() -> Sequence[Tuple[str, Callable[..., bool], str]]:
    """Input for ignore cells test case using .nbqa.ini configuration."""
    nbqa_config_file = ".nbqa.ini"
    return [
        (
            "[flake8]\nignore_cells=%%%%custommagic",
            _validate_ignore_cells_with_warning,
            nbqa_config_file,
        ),
        (
            "[flake8]\nignore_cells=%%%%custommagic,%%%%anothercustommagic",
            _validate_ignore_cells_without_warning,
            nbqa_config_file,
        ),
    ]


def _ignore_cells_toml_input() -> Sequence[Tuple[str, Callable[..., bool], str]]:
    """Input for ignore cells test case using pyproject.toml configuration."""
    toml_config_file = "pyproject.toml"
    return [
        (
            '[tool.nbqa.ignore_cells]\nflake8=["%%custommagic"]',
            _validate_ignore_cells_with_warning,
            toml_config_file,
        ),
        (
            '[tool.nbqa.ignore_cells]\nflake8=["%%custommagic", "%%anothercustommagic"]',
            _validate_ignore_cells_without_warning,
            toml_config_file,
        ),
    ]


@pytest.mark.parametrize(
    "config, validate, config_file",
    [
        *_ignore_cells_cli_input(),
        *_ignore_cells_ini_input(),
        *_ignore_cells_toml_input(),
    ],
)
def test_ignore_cells(
    config: str,
    validate: Callable[..., bool],
    config_file: Optional[str],
    tmpdir: "LocalPath",
    capsys: "CaptureFixture",
) -> None:
    """Validate we can ignore custom cell magics configured via cli, .ini and .toml."""
    test_nb_path = _copy_notebook(
        Path("tests/data/notebook_with_other_magics.ipynb"), Path(tmpdir)
    )
    nbqa_args = ["flake8", str(test_nb_path)]

    if config_file:
        _create_ignore_cell_config(Path(tmpdir) / config_file, config)
    else:
        nbqa_args.append(config)

    with pytest.raises(SystemExit):
        main(nbqa_args)

    out, _ = capsys.readouterr()
    assert validate(out, test_nb_path)


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

    with pytest.raises(SystemExit):
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

    with pytest.raises(SystemExit):
        main(["flake8", str(test_nb_path), config])

    out, _ = capsys.readouterr()
    assert validate(out, test_nb_path)
