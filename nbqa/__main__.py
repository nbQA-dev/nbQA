"""Run third-party tool (e.g. :code:`mypy`) against notebook or directory."""
import os
import re
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path
from textwrap import dedent
from typing import (
    Dict,
    Iterator,
    Mapping,
    MutableMapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from pkg_resources import parse_version

from nbqa import config_parser, replace_source, save_source
from nbqa.cmdline import CLIArgs
from nbqa.config.config import Configs
from nbqa.find_root import find_project_root
from nbqa.notebook_info import NotebookInfo
from nbqa.optional import metadata
from nbqa.output_parser import Output, map_python_line_to_nb_lines
from nbqa.path_utils import get_relative_and_absolute_paths, remove_suffix
from nbqa.text import BOLD, RESET

BASE_ERROR_MESSAGE = (
    f'{BOLD}nbQA failed to process {{notebook}} with exception "{{exp}}"{RESET}\n'
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


class TemporaryFile(NamedTuple):
    """Temporary file and file descriptor."""

    fd: int
    file: str


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
    if not os.path.isdir(root_dir):
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
) -> Iterator[str]:
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
        str(notebook)
        for notebook in notebooks
        if include_re.search(str(notebook.as_posix()))
        if not exclude_re.search(str(notebook.as_posix()))
    )


def _get_all_notebooks(
    root_dirs: Sequence[str], files: Optional[str], exclude: Optional[str]
) -> Iterator[str]:
    """
    Get generator with all notebooks passed in via the command-line, applying exclusions.

    Parameters
    ----------
    root_dirs
        All the notebooks/directories passed in via the command-line.
    files
        Pattern of files to include.
    exclude
        Pattern of files to exclude.

    Returns
    -------
    Iterator
        All Jupyter Notebooks found in all passed directories/notebooks.
    """
    return _filter_by_include_exclude(
        (j for i in root_dirs for j in _get_notebooks(i)), files, exclude
    )


def _replace_temp_python_file_references_in_out_err(
    temp_python_file: str,
    notebook: str,
    out: str,
    err: str,
) -> Output:
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

    Returns
    -------
    Output
        Stdout, stderr with temporary directory replaced by current working directory.
    """
    py_basename = os.path.basename(temp_python_file)
    nb_basename = os.path.basename(notebook)
    out = out.replace(py_basename, nb_basename)
    err = err.replace(py_basename, nb_basename)

    out = out.replace(
        remove_suffix(py_basename, ".py"), remove_suffix(nb_basename, ".ipynb")
    )
    err = err.replace(
        remove_suffix(py_basename, ".py"), remove_suffix(nb_basename, ".ipynb")
    )

    return Output(out, err)


def _get_mtimes(arg: str) -> Set[float]:
    """
    Get the modification times of any converted notebooks.

    Parameters
    ----------
    arg
        Notebook to run 3rd party tool on.

    Returns
    -------
    Set
        Modification times of any converted notebooks.
    """
    return {os.path.getmtime(arg)}


def _run_command(
    command: str,
    cmd_args: Sequence[str],
    args: Sequence[str],
) -> Tuple[Output, int, bool]:
    """
    Run third-party tool against given file or directory.

    Parameters
    ----------
    command
        Third-party tool (e.g. :code:`mypy`) to run against notebook.
    cmd_args
        Flags to pass to third-party tool (e.g. :code:`--verbose`).
    args
        Notebooks, or directories of notebooks, third-party tool is being run on.

    Returns
    -------
    output
        Captured stdout, stderr from running third-party tool.
    output_code
        Return code from third-party tool.
    mutated
        Whether 3rd party tool modified any files.

    Raises
    ------
    ValueError
        If third-party tool isn't found in system.
    """
    before = [_get_mtimes(i) for i in args]

    output = subprocess.run(
        [sys.executable, "-m", command, *args, *cmd_args],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True,  # from Python3.7 this can be replaced with `text`
    )

    mutated = [_get_mtimes(i) for i in args] != before

    output_code = output.returncode

    out = output.stdout
    err = output.stderr

    return Output(out, err), output_code, mutated


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


def _clean_up_tmp_files(nb_to_py_mapping: Mapping[str, Tuple[int, str]]) -> None:
    """Remove temporary files."""
    for file_descriptor, tmp_path in nb_to_py_mapping.values():
        try:
            os.close(file_descriptor)
        except OSError:
            # was already closed
            pass
        os.remove(tmp_path)


def _get_nb_to_py_mapping(
    root_dirs: Sequence[str], files: Optional[str], exclude: Optional[str]
) -> Dict[str, TemporaryFile]:
    """
    Get mapping between notebooks and temporary Python files.

    Parameters
    ----------
    root_dirs
        All the notebooks/directories passed in via the command-line.
    files
        Pattern of files to include.
    exclude
        Pattern of files to exclude.

    Returns
    -------
    Dict[str, Tuple[int, str]]
        Mapping between notebooks and temporary Python files.

    Raises
    ------
    FileNotFoundError
        If notebook isn't found.
    """
    nb_to_py_mapping: Dict[str, TemporaryFile] = {}
    for notebook in _get_all_notebooks(root_dirs, files, exclude):
        if not os.path.exists(notebook):
            _clean_up_tmp_files(nb_to_py_mapping)
            raise FileNotFoundError(
                f"{BOLD}No such file or directory: {notebook}{RESET}\n"
            )

        nb_to_py_mapping[notebook] = TemporaryFile(
            *tempfile.mkstemp(
                dir=os.path.dirname(notebook),
                prefix=remove_suffix(os.path.basename(notebook), ".ipynb"),
                suffix=".py",
            )
        )
        relative_path, _ = get_relative_and_absolute_paths(
            nb_to_py_mapping[notebook].file
        )
        nb_to_py_mapping[notebook] = nb_to_py_mapping[notebook]._replace(
            file=relative_path
        )
    return nb_to_py_mapping


def _main(  # pylint: disable=R0912,R0914,R0911
    cli_args: CLIArgs, configs: Configs
) -> int:
    """
    Run third-party tool on a single notebook or directory.

    Parameters
    ----------
    cli_args
        Commanline arguments passed to nbqa.
    configs
        Configuration passed to nbqa from commandline or via a config file

    Returns
    -------
    int
        Output code from third-party tool.
    """
    try:
        nb_to_py_mapping = _get_nb_to_py_mapping(
            cli_args.root_dirs, configs.nbqa_files, configs.nbqa_exclude
        )
    except FileNotFoundError as exc:
        sys.stderr.write(str(exc))
        return 1

    failed_notebooks = {}
    try:  # pylint disable=R0912

        if not nb_to_py_mapping:
            sys.stderr.write(
                "No .ipynb notebooks found in given directories: "
                f"{' '.join(i for i in cli_args.root_dirs if os.path.isdir(i))}\n"
            )
            return 0

        nb_info_mapping: MutableMapping[str, NotebookInfo] = {}

        for notebook, (file_descriptor, _) in nb_to_py_mapping.items():
            try:
                nb_info_mapping[notebook] = save_source.main(
                    notebook,
                    file_descriptor,
                    configs.nbqa_process_cells,
                    cli_args.command,
                    skip_bad_cells=configs.nbqa_skip_cells,
                )
            except Exception as exp_repr:  # pylint: disable=W0703
                failed_notebooks[notebook] = repr(exp_repr)

        if len(failed_notebooks) == len(nb_to_py_mapping):
            sys.stderr.write("No valid .ipynb notebooks found\n")
            return 123

        output, output_code, mutated = _run_command(
            cli_args.command,
            configs.nbqa_addopts,
            [
                i.file
                for key, i in nb_to_py_mapping.items()
                if key not in failed_notebooks
            ],
        )

        actually_mutated = False
        for notebook, (_, temp_python_file) in nb_to_py_mapping.items():
            if notebook in failed_notebooks:
                continue
            output = _replace_temp_python_file_references_in_out_err(
                temp_python_file, notebook, output.out, output.err
            )
            output = map_python_line_to_nb_lines(
                cli_args.command,
                output.out,
                output.err,
                notebook,
                nb_info_mapping[notebook].cell_mappings,
            )

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
                    sys.stderr.write(msg)
                    return 1

                try:
                    actually_mutated = (
                        REPLACE_FUNCTION[configs.nbqa_diff](
                            temp_python_file,
                            notebook,
                            nb_info_mapping[notebook],
                        )
                        or actually_mutated
                    )
                except Exception as exp_repr:  # pylint: disable=W0703
                    failed_notebooks[notebook] = repr(exp_repr)

        sys.stdout.write(output.out)
        sys.stderr.write(output.err)

        if mutated and not actually_mutated:
            output_code = 0
            mutated = False

        if failed_notebooks:
            output_code = 123
            sys.stderr.write("\n")
            # https://github.com/python/mypy/issues/5080
            for failure, exp_repr in failed_notebooks.items():  # type: ignore
                sys.stderr.write(
                    BASE_ERROR_MESSAGE.format(notebook=failure, exp=exp_repr)  # type: ignore
                )
            sys.stderr.write(
                f"{BOLD}\n"
                "If you believe the notebook(s) to be valid, please "
                f"report a bug at https://github.com/nbQA-dev/nbQA/issues {RESET}\n"
            )
            sys.stderr.write("\n")

        if configs.nbqa_diff:
            if mutated:
                sys.stdout.write(
                    "To apply these changes use `--nbqa-mutate` instead of `--nbqa-diff`\n"
                )
            return output_code

    finally:
        _clean_up_tmp_files(nb_to_py_mapping)
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


def main(argv: Optional[Sequence[str]] = None) -> int:
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

    return _main(cli_args, configs)


if __name__ == "__main__":
    sys.exit(main())
