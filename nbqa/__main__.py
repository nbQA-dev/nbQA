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
from typing import Iterator, Mapping, MutableMapping, Optional, Sequence, Set, Tuple

from pkg_resources import parse_version

from nbqa import config_parser, replace_source, save_source
from nbqa.cmdline import CLIArgs
from nbqa.config.config import CONFIG_FILES, Configs
from nbqa.find_root import find_project_root
from nbqa.notebook_info import NotebookInfo
from nbqa.optional import metadata
from nbqa.output_parser import map_python_line_to_nb_lines
from nbqa.text import BOLD, RESET

BASE_ERROR_MESSAGE = dedent(
    f"""\
    {BOLD}{{}}
    Please report a bug at https://github.com/nbQA-dev/nbQA/issues {RESET}
    """
)
MIN_VERSIONS = {"isort": "5.3.0"}
VIRTUAL_ENVIRONMENTS_URL = (
    "https://realpython.com/python-virtual-environments-a-primer/"
)
EXCLUDES = (
    r"/("
    r"\.direnv|\.eggs|\.git|\.hg|\.ipynb_checkpoints|\.mypy_cache|\.nox|\.svn|\.tox|\.venv|"
    r"_build|buck-out|build|dist|venv"
    r")/"
)


REPLACE_FUNCTION = {
    True: replace_source.diff,
    False: replace_source.mutate,
}


class UnsupportedPackageVersionError(Exception):
    """Raise if installed module is older than minimum required version."""

    def __init__(self, command: str, current_version: str, min_version: str) -> None:
        """Initialise with command, current version, and minimum version."""
        self.msg = (
            f"{BOLD}nbqa only works with {command} >= {min_version}, "
            f"while you have {current_version} installed.{RESET}"
        )
        super().__init__(self.msg)


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
        i
        for i in Path(root_dir).rglob("*.ipynb")
        if not re.search(EXCLUDES, str(i.resolve().as_posix()))
    )


def _filter_by_include_exclude(
    notebooks: Iterator[Path],
    include: Optional[str],
    exclude: Optional[str],
) -> Iterator[Path]:
    """
    Include files which match include, exclude those matching exclude.

    notebooks
        Notebooks (not directories) to run code quality tool on.
    include:
        Global file include pattern.
    exclude:
        Global file exclude pattern.

    Returns
    -------
    Iterator
        Notebooks matching include and not matching exclude.
    """
    include = include or ""
    exclude = exclude or "^$"
    include_re, exclude_re = re.compile(include), re.compile(exclude)
    return (
        notebook
        for notebook in notebooks
        if include_re.search(str(notebook.as_posix()))
        if not exclude_re.search(str(notebook.as_posix()))
    )


def _get_all_notebooks(
    root_dirs: Sequence[str], files: Optional[str], exclude: Optional[str]
) -> Iterator[Path]:
    """
    Get generator with all notebooks passed in via the command-line, applying exclusions.

    Parameters
    ----------
    root_dirs
        All the notebooks/directories passed in via the command-line.

    Returns
    -------
    Iterator
        All Jupyter Notebooks found in all passed directories/notebooks.
    """
    return _filter_by_include_exclude(
        (j for i in root_dirs for j in _get_notebooks(i)), files, exclude
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

    Raises
    ------
    FileNotFoundError
        If notebook doesn't exist.
    """
    if not notebook.exists():
        raise FileNotFoundError(
            f"{BOLD}No such file or directory: {str(notebook)}{RESET}"
        )
    relative_notebook_path = (
        notebook.resolve().relative_to(project_root).with_suffix(".py")
    )
    temp_python_file = Path(tmpdir) / relative_notebook_path
    temp_python_file.parent.mkdir(parents=True, exist_ok=True)
    return temp_python_file


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

    out = out.replace(f"{tmpdirname}{os.sep}", "")
    err = err.replace(f"{tmpdirname}{os.sep}", "")

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
        init_file = Path(os.path.join(*parts[:idx])) / "__init__.py"
        Path(tmpdirname).joinpath(init_file).parent.mkdir(parents=True, exist_ok=True)
        Path(tmpdirname).joinpath(init_file).touch()


def _preserve_config_files(
    config_files: Sequence[str], tmpdirname: str, project_root: Path
) -> None:
    """
    Copy local config file to temporary directory.

    Parameters
    ----------
    config_files
        Config files for third-party tool (e.g. mypy).
    tmpdirname
        Temporary directory to store converted notebooks in.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.
    """
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
    nb_to_py_mapping: Mapping[Path, Path],
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
        return Path(tmpdirname) / Path(root_dir).resolve().relative_to(project_root)
    return nb_to_py_mapping[Path(root_dir)]


def _get_all_args(
    root_dirs: Sequence[str],
    tmpdirname: str,
    nb_to_py_mapping: Mapping[Path, Path],
    project_root: Path,
) -> Sequence[Path]:
    """
    Get all arguments to run command against.

    Parameters
    ----------
    root_dirs
        All notebooks or directories third-party tool is being run against.
    tmpdirname
        Temporary directory where converted notebooks are stored.
    nb_to_py_mapping
        Mapping between notebooks and Python files corresponding to converted notebooks.
    project_root
        Root of repository, where .git / .hg / .nbqa.ini file is.

    Returns
    -------
    Sequence[Path]
        All notebooks or directories to run third-party tool against.
    """
    return [_get_arg(i, tmpdirname, nb_to_py_mapping, project_root) for i in root_dirs]


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
    cmd_args: Sequence[str],
    args: Sequence[Path],
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
    args
        Notebooks, or directories of notebooks, third-party tool is being run on.

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
        "MYPYPATH"
    ] = f"{env.get('MYPYPATH', '').rstrip(os.pathsep)}{os.pathsep}{os.getcwd()}"

    env[
        "PYTHONPATH"
    ] = f"{env.get('PYTHONPATH', '').rstrip(os.pathsep)}{os.pathsep}{os.getcwd()}"

    before = [_get_mtimes(i) for i in args]

    output = subprocess.run(
        [sys.executable, "-m", command, *(str(i) for i in args), *cmd_args],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=tmpdirname,
        env=env,
        universal_newlines=True,  # from Python3.7 this can be replaced with `text`
    )

    mutated = [_get_mtimes(i) for i in args] != before

    output_code = output.returncode

    out = output.stdout
    err = output.stderr

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
        f"""\
        {BOLD}Command `{command}` not found by nbqa.{RESET}

        Please make sure you have it installed in the same Python environment as nbqa. See
        e.g. {VIRTUAL_ENVIRONMENTS_URL} for how to set up
        a virtual environment in Python.

        Since nbqa is installed at {{nbqa_loc}} and uses the Python executable found at
        {{python}}, you could fix this issue by running `{{python}} -m pip install {command}`.
        """
    )
    python_executable = sys.executable
    nbqa_loc = str(Path(sys.modules["nbqa"].__file__).parent)

    return template.format(python=python_executable, nbqa_loc=nbqa_loc)


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

    return cli_config.merge(Configs.get_default_config(cli_args.command))


def _run_on_one_root_dir(
    cli_args: CLIArgs, configs: Configs, project_root: Path
) -> int:
    """
    Run third-party tool on a single notebook or directory.

    Parameters
    ----------
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
            for notebook in _get_all_notebooks(
                cli_args.root_dirs, configs.nbqa_files, configs.nbqa_exclude
            )
        }

        if not nb_to_py_mapping:
            sys.stderr.write(
                "No .ipynb notebooks found in given directories: "
                f"{' '.join(i for i in cli_args.root_dirs if Path(i).is_dir())}\n"
            )
            return 0

        config_files = (
            [configs.nbqa_config]
            if configs.nbqa_config
            else CONFIG_FILES[cli_args.command]
        )
        _preserve_config_files(config_files, tmpdirname, project_root)

        nb_info_mapping: MutableMapping[Path, NotebookInfo] = {}

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
            _get_all_args(
                cli_args.root_dirs, tmpdirname, nb_to_py_mapping, project_root
            ),
        )

        for notebook, temp_python_file in nb_to_py_mapping.items():
            out, err = _replace_temp_python_file_references_in_out_err(
                tmpdirname, temp_python_file, notebook, out, err
            )
            try:
                out, err = map_python_line_to_nb_lines(
                    cli_args.command,
                    out,
                    err,
                    notebook,
                    nb_info_mapping[notebook].cell_mappings,
                )
            except Exception as exc:  # pylint: disable=W0703
                msg = (
                    f"{repr(exc)} while parsing output "
                    f"from applying {cli_args.command} to {str(notebook)}"
                )
                sys.stderr.write(BASE_ERROR_MESSAGE.format(msg))

            if mutated:
                if not configs.nbqa_mutate and not configs.nbqa_diff:
                    # pylint: disable=C0301
                    msg = dedent(
                        f"""\
                        {BOLD}Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag, e.g.:{RESET}

                            nbqa {cli_args.command} notebook.ipynb --nbqa-mutate

                        or, to only preview changes, use the `--nbqa-diff` flag, e.g.:

                            nbqa {cli_args.command} notebook.ipynb --nbqa-diff
                        """
                    )
                    # pylint: enable=C0301
                    raise SystemExit(msg)

                try:
                    REPLACE_FUNCTION[configs.nbqa_diff](
                        temp_python_file,
                        notebook,
                        nb_info_mapping[notebook],
                    )
                except Exception as exc:
                    raise RuntimeError(
                        BASE_ERROR_MESSAGE.format(
                            f"Error reconstructing {str(notebook)}"
                        )
                    ) from exc

        if configs.nbqa_diff:
            if mutated:
                sys.stdout.write(
                    "To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`\n"
                )
            return 0

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
    UnsupportedPackageVersionError
        If third-party tool is of an unsupported version.
    """
    try:
        command_version = metadata.version(command)  # type: ignore
    except metadata.PackageNotFoundError:  # type: ignore
        try:
            import_module(command)
        except ImportError as exc:
            raise ModuleNotFoundError(_get_command_not_found_msg(command)) from exc
    else:
        if command in MIN_VERSIONS:
            min_version = MIN_VERSIONS[command]
            if parse_version(command_version) < parse_version(min_version):
                raise UnsupportedPackageVersionError(
                    command, command_version, min_version
                )


def main(argv: Optional[Sequence[str]] = None) -> None:
    """
    Run third-party tool (e.g. :code:`mypy`) against notebook or directory.

    Parameters
    ----------
    argv
        Command-line arguments (if calling this function directly), defaults to
        :code:`None` if calling via command-line.
    """
    cli_args: CLIArgs = CLIArgs.parse_args(argv)
    _check_command_is_installed(cli_args.command)
    project_root: Path = find_project_root(tuple(cli_args.root_dirs))
    configs: Configs = _get_configs(cli_args, project_root)
    configs.validate()

    output_code = _run_on_one_root_dir(cli_args, configs, project_root)

    sys.exit(output_code)


if __name__ == "__main__":
    main()
