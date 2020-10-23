"""Run third-party tool (e.g. :code:`mypy`) against notebook or directory."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path
from textwrap import dedent
from typing import Dict, Iterator, List, Mapping, Match, Optional, Set, Tuple

from nbqa import config_parser, replace_source, save_source
from nbqa.cmdline import CLIArgs
from nbqa.config import Configs
from nbqa.find_root import find_project_root
from nbqa.notebook_info import NotebookInfo

CONFIG_FILES = ["setup.cfg", "tox.ini", "pyproject.toml"]

BASE_ERROR_MESSAGE = dedent(
    """

    😭 {} 😭

    Please report a bug at https://github.com/nbQA-dev/nbQA/issues 🙏
    """
)


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
        return iter((Path(root_dir),))
    return (
        i for i in Path(root_dir).rglob("*.ipynb") if ".ipynb_checkpoints" not in str(i)
    )


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
    relative_notebook_path = (
        notebook.resolve().relative_to(project_root).with_suffix(".py")
    )
    temp_python_file = Path(tmpdir) / relative_notebook_path
    temp_python_file.parent.mkdir(parents=True, exist_ok=True)
    return temp_python_file


def _map_python_line_to_nb_lines(
    out: str, notebook: Path, cell_mapping: Mapping[int, str]
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
    str
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
    tmpdirname: str,
    temp_python_file: Path,
    notebook: Path,
    out: str,
    err: str,
) -> Tuple[str, str]:
    """
    Replace references to temporary Python file with references to notebook.

    Parameters
    ----------
    tmpdirname
        Temporary directory used for converting notebooks to python files
    temp_python_file
        Temporary Python file where notebook was converted to.
    notebook
        Original Jupyter notebook.
    out
        Captured stdout from third-party tool.
    err
        Captured stderr from third-party tool.

    Returns
    -------
    out
        Stdout with temporary directory replaced by current working directory.
    err
        Stderr with temporary directory replaced by current working directory.
    """
    # 1. Relative path is used because some tools like pylint always report only
    # the relative path of the file(relative to project root),
    # though absolute path was passed as the input.
    # 2. This `resolve()` part is necessary to handle cases when the path used
    # is a symlink as well as no normalize the path.
    # I couldn't reproduce this locally, but during CI, on the Windows job, I found
    # that VSSADM~1 was changing into VssAdministrator.
    paths = (
        str(path)
        for path in [
            temp_python_file,
            temp_python_file.resolve(),
            temp_python_file.relative_to(tmpdirname),
        ]
    )

    notebook_path = str(notebook)
    for path in paths:
        out = out.replace(path, notebook_path)
        err = err.replace(path, notebook_path)

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
    config_files = [nbqa_config] if nbqa_config is not None else CONFIG_FILES
    for config_file in config_files:
        config_file_path = project_root / config_file
        if config_file_path.exists():
            target_location = Path(tmpdirname) / config_file_path.resolve().relative_to(
                project_root
            )
            target_location.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(
                str(config_file_path),
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
    ...     Path('my_notebook.ipynb'): Path('tmpdir').joinpath('my_notebook.py')
    ... }
    >>> _get_arg(root_dir, tmpdirname, nb_to_py_mapping).as_posix()
    'tmpdir/my_notebook.py'
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
    return {os.path.getmtime(str(i)) for i in arg.rglob("*.py")}


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
    arg
        Notebook, or directory of notebooks, third-party tool is being run on.

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
    env[
        "PYTHONPATH"
    ] = f"{env.get('PYTHONPATH', '').rstrip(os.pathsep)}{os.pathsep}{os.getcwd()}"

    before = _get_mtimes(arg)

    output = subprocess.run(
        [sys.executable, "-m", command, str(arg), *cmd_args],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=tmpdirname,
        env=env,
    )

    mutated = _get_mtimes(arg) != before

    output_code = output.returncode

    out = output.stdout.decode()
    err = output.stderr.decode()

    return out, err, output_code, mutated


def _get_command_not_found_msg(command: str) -> str:
    """Return the message to display when the command is not found by nbqa.

    Parameters
    ----------
    command : str
        Command passed to nbqa to find.

    Returns
    -------
    str
        Message to display to stdout.
    """
    template = dedent(
        """\
        Command `{command}` not found by nbqa.

        Please make sure you have it installed in the same Python environment as nbqa. See
        e.g. https://realpython.com/python-virtual-environments-a-primer/ for how to set up
        a virtual environment in Python.

        Since nbqa is installed at {nbqa_loc} and uses the Python executable found at
        {python}, you could fix this issue by running `{python} -m pip install {command}`.
        """
    )
    python_executable = sys.executable
    nbqa_loc = str(Path(sys.modules["nbqa"].__file__).parent)

    return template.format(command=command, python=python_executable, nbqa_loc=nbqa_loc)


def _get_configs(cli_args: CLIArgs, project_root: Path) -> Configs:
    """
    Deal with extra configs for 3rd party tool.

    Parameters
    ----------
    cli_args
        Commandline arguments passed to nbqa
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    Configs
        Taken from CLI (if given), else from .nbqa.ini.
    """
    cli_config: Configs = Configs.parse_from_cli_args(cli_args)
    file_config: Optional[Configs] = config_parser.parse_config_from_file(
        cli_args, project_root
    )

    if file_config is not None:
        cli_config = cli_config.merge(file_config)

    return cli_config


def _run_on_one_root_dir(
    root_dir: str, cli_args: CLIArgs, configs: Configs, project_root: Path
) -> int:
    """
    Run third-party tool on a single notebook or directory.

    Parameters
    ----------
    root_dir
        Directory on which nbqa should be run
    cli_args
        Commanline arguments passed to nbqa.
    configs
        Configuration passed to nbqa from commandline or via a config file
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    int
        Output code from third-party tool.

    Raises
    ------
    RuntimeError
        If unable to parse or reconstruct notebook.
    SystemExit
        If third-party tool would've reformatted notebook but ``--nbqa-mutate``
        wasn't passed.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:

        nb_to_py_mapping = {
            notebook: _temp_python_file_for_notebook(notebook, tmpdirname, project_root)
            for notebook in _get_notebooks(root_dir)
        }

        _preserve_config_files(configs.nbqa_config, tmpdirname, project_root)

        nb_info_mapping: Dict[Path, NotebookInfo] = {}

        for notebook, temp_python_file in nb_to_py_mapping.items():
            try:
                nb_info_mapping[notebook] = save_source.main(
                    notebook,
                    temp_python_file,
                    configs.nbqa_ignore_cells,
                    cli_args.command,
                )
            except Exception as exc:
                raise RuntimeError(
                    BASE_ERROR_MESSAGE.format(f"Error parsing {str(notebook)}")
                ) from exc

            _create_blank_init_files(notebook, tmpdirname, project_root)

        out, err, output_code, mutated = _run_command(
            cli_args.command,
            tmpdirname,
            configs.nbqa_addopts,
            _get_arg(root_dir, tmpdirname, nb_to_py_mapping, project_root),
        )

        for notebook, temp_python_file in nb_to_py_mapping.items():
            out, err = _replace_temp_python_file_references_in_out_err(
                tmpdirname, temp_python_file, notebook, out, err
            )
            out = _map_python_line_to_nb_lines(
                out, notebook, nb_info_mapping[notebook].cell_mappings
            )

            if mutated:
                if not configs.nbqa_mutate:
                    msg = dedent(
                        f"""\
                        💥 Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

                            {" ".join([str(cli_args), "--nbqa-mutate"])}
                        """
                    )
                    raise SystemExit(msg)

                try:
                    replace_source.main(
                        temp_python_file, notebook, nb_info_mapping[notebook]
                    )
                except Exception as exc:
                    raise RuntimeError(
                        BASE_ERROR_MESSAGE.format(
                            f"Error reconstructing {str(notebook)}"
                        )
                    ) from exc

        sys.stdout.write(out)
        sys.stderr.write(err)

    return output_code


def _check_command_is_installed(command: str) -> None:
    """
    Check whether third-party tool is installed.

    Parameters
    ----------
    command
        Third-party tool being run on notebook(s).

    Raises
    ------
    ModuleNotFoundError
        If third-party tool isn't installed.
    """
    try:
        import_module(command)
    except ImportError as exc:
        raise ModuleNotFoundError(_get_command_not_found_msg(command)) from exc


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
    configs: Configs = _get_configs(cli_args, project_root)

    _check_command_is_installed(cli_args.command)

    output_codes = [
        _run_on_one_root_dir(i, cli_args, configs, project_root)
        for i in cli_args.root_dirs
    ]

    sys.exit(int(any(output_codes)))


if __name__ == "__main__":
    main()
