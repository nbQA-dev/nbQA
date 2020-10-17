"""Check user can check for other magics."""
import json
import os
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple

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
    expected = "".join(f"{str(test_nb_path)}:{i}{os.linesep}" for i in expected_out)
    return expected == actual


def _validate_ignore_cells_without_warning(actual: str, _: Path) -> bool:
    """Validate the results of notebooks without warnings."""
    expected = ""
    return expected == actual


def _ignore_cells_cli_input() -> List[Tuple[str, Callable[..., bool], Optional[str]]]:
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


def _ignore_cells_ini_input() -> List[Tuple[str, Callable[..., bool], str]]:
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


def _ignore_cells_toml_input() -> List[Tuple[str, Callable[..., bool], str]]:
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


def _indented_magics_toml_input() -> List[Tuple[str, Callable[..., bool], str]]:
    """Input for handling indented magics test case using toml configuration."""
    toml_config_file = "pyproject.toml"

    return [
        (
            "[tool.nbqa.mutate]\nblack=1",
            _validate_indented_magics,
            toml_config_file,
        )
    ]


def _validate_indented_magics(actual: str, test_nb_path: Path) -> bool:
    """Validate the results of the notebook with indented magics after running black."""
    expected_cell_source = [
        ["import time\n", "\n", 'print(f"current_time: {time.time()}")'],
        [
            "from random import randint\n",
            "\n",
            "if randint(5, 10) > 8:\n",
            '    %time print("Hello world")',
        ],
        ["str.split??"],
        ["# indented line magic\n", "?str.splitlines"],
        ["%time randint(5, 10)"],
    ]
    result: bool = True

    actual_cells = json.loads(test_nb_path.read_text())["cells"]
    actual_cell_source = (cell["source"] for cell in actual_cells)

    for actual_src, expected_src in zip(actual_cell_source, expected_cell_source):
        result = result and (actual_src == expected_src)

    return result and (actual == "")


@pytest.mark.parametrize(
    "config, validate, config_file",
    [*_indented_magics_toml_input()],
)
def test_indented_magics(
    config: str,
    validate: Callable[..., bool],
    config_file: Optional[str],
    tmpdir: "LocalPath",
    capsys: "CaptureFixture",
) -> None:
    """Check if the indented line magics are retained properly after mutating."""
    test_nb_path = _copy_notebook(
        Path("tests/data/notebook_with_indented_magics.ipynb"), Path(tmpdir)
    )

    nbqa_args = ["black", str(test_nb_path)]

    if config_file:
        _create_ignore_cell_config(Path(tmpdir) / config_file, config)
    else:
        nbqa_args.append(config)

    with pytest.raises(SystemExit):
        main(nbqa_args)

    out, _ = capsys.readouterr()
    assert validate(out, test_nb_path)
