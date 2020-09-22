"""Run third-party tool (e.g. :code:`mypy`) against notebook or directory."""

import configparser
import os
import re
import shutil
import subprocess
import sys
import tempfile
from configparser import ConfigParser
from pathlib import Path
from shlex import split
from textwrap import dedent
from typing import Dict, Iterator, List, Match, NamedTuple, Optional, Set, Tuple

from nbqa import replace_source, save_source
from nbqa.cmdline import CLIArgs
from nbqa.find_root import find_project_root

CONFIG_FILES = ["setup.cfg", "tox.ini", "pyproject.toml"]
NBQA_CONFIG_SECTION = ["config", "mutate", "addopts"]
CONFIG_PREFIX = "nbqa."
HISTORIC_CONFIG_FILE = ".nbqa.ini"

CONFIG_FILES = ["setup.cfg", "tox.ini", "pyproject.toml"]


class Configs(NamedTuple):
    """
    Options with which to run nbqa.

    Attributes
    ----------
    allow_mutation
        Whether to allow nbqa to modify notebooks.
    config
        Configuration of the third party tool.
    ignore_cells
        Extra cells which nbqa should ignore.
    addopts
        Additional arguments passed to the third party tool
    """

    allow_mutation: bool
    config: Optional[str]
    ignore_cells: Optional[str]
    addopts: List[str]


def _get_notebooks(root_dir: str) -> Iterator[Path]:
    """
    Get generator with all notebooks in directory.

    Parameters
    ----------
    root_dir
        Notebook or directory to run third-party tool on.

    Returns
    -------
    notebooks
        All Jupyter Notebooks found in directory.
    """
    if not Path(root_dir).is_dir():
        return (i for i in (Path(root_dir),))
    notebooks = (
        i for i in Path(root_dir).rglob("*.ipynb") if ".ipynb_checkpoints" not in str(i)
    )
    return notebooks


def _temp_python_file_for_notebook(
    notebook: Path, tmpdir: str, project_root: Path
) -> Path:
    """
    Get temporary file to save converted notebook into.

    Parameters
    ----------
    notebook
        Notebook that third-party tool will be run on.
    tmpdir
        Temporary directory where converted notebooks will be saved.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    Path
        Temporary Python file whose location mirrors that of the notebook, but
        inside the temporary directory.
    """
    # Add 3 extra whitespaces because `ipynb` is 3 chars longer than `py`.
    relative_notebook_dir = notebook.resolve().relative_to(project_root).parent
    temp_python_file = Path(tmpdir) / relative_notebook_dir / f"{notebook.stem}   .py"
    temp_python_file.parent.mkdir(parents=True, exist_ok=True)
    return temp_python_file


def _replace_full_path_out_err(
    out: str, err: str, temp_python_file: Path, notebook: Path
) -> Tuple[str, str]:
    """
    Replace references to temporary Python file's full path with notebook's path.

    Parameters
    ----------
    out
        Captured stdout from third-party tool.
    err
        Captured stderr from third-party tool.
    temp_python_file
        Temporary Python file where notebook was converted to.
    notebook
        Original Jupyter notebook.

    Returns
    -------
    out
        Stdout with temporary Python file's full path with notebook's path.
    err
        Stderr with temporary Python file's full path with notebook's path.
    """
    out = out.replace(str(temp_python_file), str(notebook.resolve()))
    err = err.replace(str(temp_python_file), str(notebook.resolve()))

    # This next part is necessary to handle cases when `resolve` changes the path.
    # I couldn't reproduce this locally, but during CI, on the Windows job, I found
    # that VSSADM~1 was changing into VssAdministrator.
    out = out.replace(str(temp_python_file.resolve()), str(notebook.resolve()))
    err = err.replace(str(temp_python_file.resolve()), str(notebook.resolve()))
    return out, err


def _replace_relative_path_out_err(out: str, notebook: Path) -> str:
    """
    Replace references to temporary Python file's relative path with notebook's path.

    Parameters
    ----------
    out
        Captured stdout from third-party tool.
    notebook
        Original Jupyter notebook.

    Returns
    -------
    out
        Stdout with temporary Python file's relative path with notebook's path.
    Examples
    --------
    >>> out = "notebook   .py ."
    >>> notebook = Path('notebook.ipynb')
    >>> _replace_relative_path_out_err(out, notebook)
    'notebook.ipynb .'
    """
    out = out.replace(
        str(notebook.parent.joinpath(f"{notebook.stem}   ").with_suffix(".py")),
        str(notebook),
    )
    return out


def _map_python_line_to_nb_lines(
    out: str, notebook: Path, cell_mapping: Dict[int, str]
) -> str:
    """
    Make sure stdout and stderr make reference to Jupyter Notebook cells and lines.

    Parameters
    ----------
    out
        Captured stdout from third-party tool.
    notebook
        Original Jupyter notebook.
    cell_mapping
        Mapping from Python file lines to Jupyter notebook cells.

    Returns
    -------
    out
        Stdout with references to temporary Python file's lines replaced with references
        to notebook's cells and lines.
    """
    pattern = rf"(?<={notebook.name}:)\d+"

    def substitution(match: Match[str]) -> str:
        """Replace Python line with corresponding Jupyter notebook cell."""
        return str(cell_mapping[int(match.group())])

    out = re.sub(pattern, substitution, out)

    # doctest pattern
    pattern = rf'(?<={notebook.name}", line )\d+'
    if re.search(pattern, out) is not None:
        out = re.sub(pattern, substitution, out)
        out = out.replace(f'{notebook.name}", line ', f'{notebook.name}", ')

    return out


def _replace_temp_python_file_references_in_out_err(
    temp_python_file: Path,
    notebook: Path,
    out: str,
    err: str,
    cell_mapping: Dict[int, str],
) -> Tuple[str, str]:
    """
    Replace references to temporary Python file with references to notebook.

    Parameters
    ----------
    temp_python_file
        Temporary Python file where notebook was converted to.
    notebook
        Original Jupyter notebook.
    out
        Captured stdout from third-party tool.
    err
        Captured stderr from third-party tool.
    cell_mapping
        Mapping from Python lines to Jupyter notebook cells.

    Returns
    -------
    out
        Stdout with temporary directory replaced by current working directory.
    err
        Stderr with temporary directory replaced by current working directory.
    """
    out, err = _replace_full_path_out_err(out, err, temp_python_file, notebook)
    out = _replace_relative_path_out_err(out, notebook)
    out = _map_python_line_to_nb_lines(out, notebook, cell_mapping)
    return out, err


def _create_blank_init_files(
    notebook: Path, tmpdirname: str, project_root: Path
) -> None:
    """
    Replicate local (possibly blank) __init__ files to temporary directory.

    Parameters
    ----------
    notebook
        Notebook third-party tool is being run against.
    tmpdirname
        Temporary directory to store converted notebooks in.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.
    """
    parts = notebook.resolve().relative_to(project_root).parts

    for idx in range(1, len(parts)):
        init_files = Path(os.path.join(*parts[:idx])).glob("__init__.py")
        for init_file in init_files:
            Path(tmpdirname).joinpath(init_file).parent.mkdir(
                parents=True, exist_ok=True
            )
            Path(tmpdirname).joinpath(init_file).touch()
            break  # Only need to copy one __init__ file.


def _preserve_config_files(
    nbqa_config: Optional[str], tmpdirname: str, project_root: Path
) -> None:
    """
    Copy local config file to temporary directory.

    Parameters
    ----------
    nbqa_config
        Config file for third-party tool (e.g. mypy).
    tmpdirname
        Temporary directory to store converted notebooks in.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.
    """
    if nbqa_config is not None:
        config_files = [nbqa_config]
    else:
        config_files = CONFIG_FILES
    for config_file in config_files:
        if not (project_root / config_file).exists():
            continue
        target_location = Path(tmpdirname) / Path(
            project_root / config_file
        ).resolve().relative_to(project_root)
        target_location.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(
            str(project_root / config_file),
            str(target_location),
        )


def _get_arg(
    root_dir: str,
    tmpdirname: str,
    nb_to_py_mapping: Dict[Path, Path],
    project_root: Path,
) -> Path:
    """
    Get argument to run command against.

    If running against a single notebook, it'll be the filepath of the converted
    notebook in the temporary directory.
    If running against a directory, it'll be the directory mirrored in the temporary
    directory.

    Parameters
    ----------
    root_dir
        Notebook or directory third-party tool is being run against.
    tmpdirname
        Temporary directory where converted notebooks are stored.
    nb_to_py_mapping
        Mapping between notebooks and Python files corresponding to converted notebooks.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    Path
        Notebook or directory to run third-party tool against.

    Examples
    --------
    >>> root_dir = "root_dir"
    >>> tmpdirname = "tmpdir"
    >>> nb_to_py_mapping = {
    ...     Path('my_notebook.ipynb'): Path('tmpdir').joinpath('my_notebook   .py')
    ... }
    >>> _get_arg(root_dir, tmpdirname, nb_to_py_mapping).as_posix()
    'tmpdir/my_notebook   .py'
    """
    if Path(root_dir).is_dir():
        arg = Path(tmpdirname) / Path(root_dir).resolve().relative_to(project_root)
    else:
        assert len(nb_to_py_mapping) == 1
        arg = next(iter(nb_to_py_mapping.values()))
    return arg


def _get_mtimes(arg: Path) -> Set[float]:
    """
    Get the modification times of any converted notebooks.

    Parameters
    ----------
    arg
        Notebook or directory to run 3rd party tool on.

    Returns
    -------
    Set
        Modification times of any converted notebooks.
    """
    if not arg.is_dir():
        return {os.path.getmtime(str(arg))}
    return {os.path.getmtime(str(i)) for i in arg.rglob("*   .py")}


def _run_command(
    command: str,
    tmpdirname: str,
    cmd_args: List[str],
    arg: Path,
) -> Tuple[str, str, int, bool]:
    """
    Run third-party tool against given file or directory.

    Parameters
    ----------
    command
        Third-party tool (e.g. :code:`mypy`) to run against notebook.
    tmpdirname
        Temporary directory where converted notebooks will be stored.
    cmd_args
        Flags to pass to third-party tool (e.g. :code:`--verbose`).
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    out
        Captured stdout from running third-party tool.
    err
        Captured stderr from running third-party tool.
    output_code
        Return code from third-party tool.
    mutated
        Whether 3rd party tool modified any files.

    Raises
    ------
    ValueError
        If third-party tool isn't found in system.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    before = _get_mtimes(arg)

    output = subprocess.run(
        ["python", "-m", command, str(arg), *cmd_args],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=tmpdirname,
        env=env,
    )

    mutated = _get_mtimes(arg) != before

    output_code = output.returncode

    out = output.stdout.decode()
    err = output.stderr.decode()

    if "No module named" in err:
        raise ValueError(
            f"Command `{command}` not found. "
            "Please make sure you have it installed before running nbQA on it."
        )

    return out, err, output_code, mutated


def _find_config_file(
    command: str, project_root: Path
) -> Tuple[Optional[str], Optional[ConfigParser], Optional[str]]:
    """
    Find config file.

    Parameters
    ----------
    command
        Third-party tool being run.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    config_file
        Name of config file.
    config
        ConfigParser object which has read in config file.
    config_prefix
        Prefix of sections in config file.
    """
    config = configparser.ConfigParser()
    for config_file in CONFIG_FILES:
        if config_file == "pyproject.toml":
            continue  # Will be supported in a future PR.
        config.read(project_root / config_file)
        for section in NBQA_CONFIG_SECTION:
            if config.has_section(f"{CONFIG_PREFIX}{section}"):
                return config_file, config, CONFIG_PREFIX
    config.read(project_root / HISTORIC_CONFIG_FILE)
    if config.has_section(command):
        return HISTORIC_CONFIG_FILE, config, ""
    return None, None, None


def _get_option(
    config_file: str, config: ConfigParser, section: str, option: str
) -> Optional[str]:
    """
    Get option from config file.

    Parameters
    ----------
    config_file
        Name of config file.
    config
        ConfigParser object which has read in config file.
    section
        e.g. config, mutate, ...
    option
        e.g. flake8, black, ...

    Returns
    -------
    str
        Parsed option.
    """
    if config_file != ".nbqa.ini":
        if config.has_section(section):
            return config[section].get(option)
    else:
        if config.has_section(option):
            return config[option].get(section)
    return None


def _get_configs(cli_args: CLIArgs, project_root: Path) -> Configs:
    """
    Deal with extra configs for 3rd party tool.

    Parameters
    ----------
    args
        Commandline arguments passed to nbqa
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    Configs
        Taken from CLI (if given), else from .nbqa.ini.
    """
    config_file, config, config_prefix = _find_config_file(
        cli_args.command, project_root
    )
    nbqa_config: Optional[str] = cli_args.nbqa_config
    allow_mutation: bool = cli_args.nbqa_mutate
    ignore_cells: Optional[str] = cli_args.nbqa_ignore_cells
    cmd_args: List[str] = list(cli_args.nbqa_addopts)

    if config is not None:
        assert config_file is not None
        assert config_prefix is not None

        addopts = _get_option(
            config_file, config, f"{config_prefix}addopts", cli_args.command
        )
        if addopts is not None:
            cmd_args.extend(split(addopts))

        if nbqa_config is None:
            nbqa_config = _get_option(
                config_file, config, f"{config_prefix}config", cli_args.command
            )

        if not allow_mutation:
            allow_mutation = bool(
                _get_option(
                    config_file, config, f"{config_prefix}mutate", cli_args.command
                )
            )

        if ignore_cells is None:
            ignore_cells = _get_option(
                config_file, config, f"{config_prefix}ignore_cells", cli_args.command
            )

    return Configs(
        allow_mutation, config=nbqa_config, ignore_cells=ignore_cells, addopts=cmd_args
    )


def _run_on_one_root_dir(root_dir: str, cli_args: CLIArgs, project_root: Path) -> int:
    """
    Run third-party tool on a single notebook or directory.

    Parameters
    ----------
    root_dir
        Directory on which nbqa should be run
    cli_args
        Commanline arguments passed to nbqa.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    int
        Output code from third-party tool.
    """
    project_root = find_project_root(tuple(cli_args.root_dirs))

    with tempfile.TemporaryDirectory() as tmpdirname:

        nb_to_py_mapping = {
            notebook: _temp_python_file_for_notebook(notebook, tmpdirname, project_root)
            for notebook in _get_notebooks(root_dir)
        }

        cell_mappings = {}
        trailing_semicolons = {}

        configs = _get_configs(cli_args, project_root)

        _preserve_config_files(configs.config, tmpdirname, project_root)

        for notebook, temp_python_file in nb_to_py_mapping.items():
            cell_mappings[notebook], trailing_semicolons[notebook] = save_source.main(
                notebook, temp_python_file, cli_args.command, configs.ignore_cells
            )
            _create_blank_init_files(notebook, tmpdirname, project_root)

        out, err, output_code, mutated = _run_command(
            cli_args.command,
            tmpdirname,
            configs.addopts,
            _get_arg(root_dir, tmpdirname, nb_to_py_mapping, project_root),
        )

        for notebook, temp_python_file in nb_to_py_mapping.items():
            out, err = _replace_temp_python_file_references_in_out_err(
                temp_python_file, notebook, out, err, cell_mappings[notebook]
            )
            if mutated:
                if not configs.allow_mutation:
                    raise SystemExit(
                        dedent(
                            f"""\
                    💥 Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

                        {" ".join([str(cli_args), "--nbqa-mutate"])}
                    """
                        )
                    )

                replace_source.main(
                    temp_python_file, notebook, trailing_semicolons[notebook]
                )

        sys.stdout.write(out)
        sys.stderr.write(err)

    return output_code


def main(raw_args: Optional[List[str]] = None) -> None:
    """
    Run third-party tool (e.g. :code:`mypy`) against notebook or directory.

    Parameters
    ----------
    raw_args
        Command-line arguments (if calling this function directly), defaults to
        :code:`None` if calling via command-line.
    """
    cli_args: CLIArgs = CLIArgs.parse_args(raw_args)
    project_root: Path = find_project_root(tuple(cli_args.root_dirs))

    output_codes = [
        _run_on_one_root_dir(i, cli_args, project_root) for i in cli_args.root_dirs
    ]

    sys.exit(int(any(output_codes)))


if __name__ == "__main__":
    main()
