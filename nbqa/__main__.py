"""Run third-party tool (e.g. :code:`mypy`) against notebook or directory."""
from __future__ import annotations

import itertools
import os
import re
import shlex
import string
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path
from shutil import which
from textwrap import dedent
from typing import Any, Iterator, Mapping, MutableMapping, NamedTuple, Sequence, cast

import tomli

from nbqa import replace_source, save_code_source, save_markdown_source
from nbqa.cmdline import CLIArgs
from nbqa.config.config import Configs, get_default_config
from nbqa.find_root import find_project_root
from nbqa.handle_magics import MagicHandler
from nbqa.notebook_info import NotebookInfo
from nbqa.optional import metadata
from nbqa.output_parser import Output, map_python_line_to_nb_lines
from nbqa.path_utils import (
    get_relative_and_absolute_paths,
    read_notebook,
    remove_suffix,
)
from nbqa.save_code_source import CODE_SEPARATOR
from nbqa.text import BOLD, RESET


def parse_version(version: str) -> tuple[int, ...]:
    """
    Parse version; split into a tuple of ints for comparison.

    Borrowed from polars, I can't tell what Python expects us to use.
    pkg_resources is deprecated apparently.
    This is only used for isort and nbqa anyway
    """
    return tuple(int(re.sub(r"\D", "", str(v))) for v in version.split("."))


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
SUFFIX = {False: ".py", True: ".md"}
COMMAND_TO_PYTHON_MODULE = {"blacken-docs": "blacken_docs"}


class TemporaryFile(NamedTuple):
    """Temporary file and file descriptor."""

    fd: int
    file: str


class SavedSources(NamedTuple):
    """Mapping between notebooks and Python files, failed notebooks, non-Python notebooks."""

    nb_info_mapping: Mapping[str, NotebookInfo]
    failed_notebooks: MutableMapping[str, str]
    non_python_notebooks: set[str]


class UnsupportedPackageVersionError(Exception):
    """Raise if installed module is older than minimum required version."""

    def __init__(self, command: str, current_version: str, min_version: str) -> None:
        """Initialise with command, current version, and minimum version."""
        self.msg = (
            f"{BOLD}nbqa only works with {command} >= {min_version}, "
            f"while you have {current_version} installed.{RESET}"
        )
        super().__init__(self.msg)


class CommandNotFoundError(Exception):
    """Raise if requested command cannot be found in $PATH."""

    def __init__(self, command: str) -> None:
        """Initialise with command."""
        self.msg = f"{BOLD}nbqa was unable to find {command}.{RESET}"
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
    try:
        import jupytext  # noqa  # pylint: disable=unused-import,import-outside-toplevel
    except ImportError:  # pragma: nocover
        jupytext_installed = False
    else:
        jupytext_installed = True
    if os.path.isfile(root_dir):
        _, ext = os.path.splitext(root_dir)
        if (jupytext_installed and ext in (".ipynb", ".md")) or (
            not jupytext_installed and ext == ".ipynb"
        ):
            return iter((Path(root_dir),))
        return iter([])

    if not os.path.exists(root_dir):
        # Process later, raise appropriate error message after clean up.
        return iter((Path(root_dir),))

    if jupytext_installed:
        iterable = itertools.chain(
            Path(root_dir).rglob("*.ipynb"), Path(root_dir).rglob("*.md")
        )
    else:  # pragma: nocover
        iterable = itertools.chain(Path(root_dir).rglob("*.ipynb"))

    return (i for i in iterable if not re.search(EXCLUDES, str(i.resolve().as_posix())))


def _filter_by_include_exclude(
    notebooks: Iterator[Path],
    include: str | None,
    exclude: str | None,
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
    root_dirs: Sequence[str], files: str | None, exclude: str | None
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
    *,
    md: bool,
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
    _, ext = os.path.splitext(notebook)
    py_basename = os.path.basename(temp_python_file)
    nb_basename = os.path.basename(notebook)
    out = out.replace(py_basename, nb_basename)
    err = err.replace(py_basename, nb_basename)

    out = out.replace(
        remove_suffix(py_basename, SUFFIX[md]), remove_suffix(nb_basename, ext)
    )
    err = err.replace(
        remove_suffix(py_basename, SUFFIX[md]), remove_suffix(nb_basename, ext)
    )

    return Output(out, err)


def _get_mtimes(arg: str) -> set[float]:
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


def _record_newlines(
    args: Sequence[str],
    first_passes: dict[str, tuple[Mapping[int, Sequence[MagicHandler]], set[int], str]],
    nb_to_tmp_mapping: dict[str, TemporaryFile],
) -> dict[str, dict[str, int]]:  # pylint: disable=too-many-locals
    """
    Record newlines after each magic.

    We record the number of newlines both before and after
    running autopep8, to be able to restore them at the end.
    """
    new_lines: dict[str, dict[str, int]] = {}
    tmp_to_nb_mapping = {val.file: key for key, val in nb_to_tmp_mapping.items()}
    for arg in args:
        temporary_lines, _, __ = first_passes[tmp_to_nb_mapping[arg]]
        replacements = [j.replacement for i in temporary_lines.values() for j in i]
        new_lines[arg] = {}
        with open(arg, encoding="utf-8") as fd:
            newlines = 0
            after_comment = False
            comment = None
            for line in fd:
                if after_comment and line == "\n":
                    newlines += 1
                elif after_comment:
                    assert comment is not None
                    new_lines[arg][comment] = newlines
                    newlines = 0
                    after_comment = False
                    comment = None
                for replacement in replacements:
                    if replacement in line:
                        after_comment = True
                        newlines = 0
                        comment = replacement
                        break
            # we've gone through all lines. If we're in 'after_comment',
            # it means there was a magic right at the end of the file.
            if after_comment:
                assert comment is not None
                new_lines[arg][comment] = newlines
    return new_lines


def _fixup_newlines(
    args: Sequence[str],
    first_passes: dict[str, tuple[Mapping[int, Sequence[MagicHandler]], set[int], str]],
    nb_to_tmp_mapping: dict[str, TemporaryFile],
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    """Run autopep8 to remove false-positives due to spaces between cells."""
    new_lines_before = _record_newlines(args, first_passes, nb_to_tmp_mapping)
    _ = subprocess.run(
        [sys.executable, "-m", "autopep8", "--select=E3", "--in-place", *args],
        capture_output=True,  # capture output to not show users irrelevant warning
    )
    new_lines_after = _record_newlines(args, first_passes, nb_to_tmp_mapping)
    return (new_lines_before, new_lines_after)


def _run_command(  # pylint: disable=too-many-locals
    command: str,
    cmd_args: Sequence[str],
    args: Sequence[str],
    *,
    shell: bool,
) -> tuple[Output, int, bool]:
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
    main_command, *sub_commands = command.split()

    my_env = os.environ.copy()
    if main_command == "mypy" and "MYPY_FORCE_COLOR" not in my_env:
        my_env["MYPY_FORCE_COLOR"] = "1"

    if shell:
        # We already checked that which does not return None

        cmd = [cast(str, which(main_command)), *shlex.split(" ".join(sub_commands))]
    else:
        python_module = COMMAND_TO_PYTHON_MODULE.get(main_command, main_command)
        cmd = [sys.executable, "-m", python_module, *sub_commands]
    before = [_get_mtimes(i) for i in args]
    output = subprocess.run(
        [*cmd, *args, *cmd_args],
        capture_output=True,
        text=False,
        env=my_env,
    )

    mutated = [_get_mtimes(i) for i in args] != before

    output_code = output.returncode

    out = output.stdout.decode()
    err = output.stderr.decode()

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
        a virtual environment in Python, and run:

            `python -m pip install {command}`.

        Note: if `{command}` isn't meant to be run as

            `python -m {command}`

        then you might want to pass `--nbqa-shell`.
        """
    )
    python_executable = sys.executable
    nbqa_file = sys.modules["nbqa"].__file__
    assert nbqa_file is not None
    nbqa_loc = str(Path(nbqa_file).parent)

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
    # start with default config.
    config = get_default_config()
    # If a section is in pyproject.toml, use that.
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.is_file():
        config_file = tomli.loads(pyproject_path.read_text("utf-8"))
        if "tool" in config_file and "nbqa" in config_file["tool"]:
            file_config = config_file["tool"]["nbqa"]
            for section in config:
                if section in file_config and cli_args.command in file_config[section]:
                    # TypedDict key must be a string literal
                    config[section] = file_config[section][cli_args.command]  # type: ignore

    # If a section was passed via CLI, use that.
    for section in config:
        if getattr(cli_args, section) is not None:
            if section == "addopts":
                # addopts are added to / overridden rather than replaced outright
                config["addopts"] = (*config["addopts"], *getattr(cli_args, section))
            else:
                # TypedDict key must be a string literal
                config[section] = getattr(cli_args, section)  # type: ignore

    # add default options
    if cli_args.command == "isort":
        config["addopts"] = (
            *config["addopts"],
            "--treat-comment-as-code",
            CODE_SEPARATOR.rstrip("\n"),
        )

    return config


def _clean_up_tmp_files(nb_to_py_mapping: Mapping[str, tuple[int, str]]) -> None:
    """Remove temporary files."""
    for file_descriptor, tmp_path in nb_to_py_mapping.values():
        try:
            os.close(file_descriptor)
        except OSError:
            # was already closed
            pass
        os.remove(tmp_path)


def _get_nb_to_tmp_mapping(
    root_dirs: Sequence[str], files: str | None, exclude: str | None, md: bool
) -> dict[str, TemporaryFile]:
    """
    Get mapping between notebooks and temporary files.

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
        Mapping between notebooks and temporary files.

    Raises
    ------
    FileNotFoundError
        If notebook isn't found.
    """
    nb_to_tmp_mapping: dict[str, TemporaryFile] = {}
    for notebook in _get_all_notebooks(root_dirs, files, exclude):
        if not os.path.exists(notebook):
            _clean_up_tmp_files(nb_to_tmp_mapping)
            raise FileNotFoundError(
                f"{BOLD}No such file or directory: {notebook}{RESET}\n"
            )

        nb_to_tmp_mapping[notebook] = TemporaryFile(
            *tempfile.mkstemp(
                dir=os.path.dirname(notebook),
                prefix=remove_suffix(
                    os.path.basename(notebook), os.path.splitext(notebook)[-1]
                ),
                suffix=SUFFIX[md],
            )
        )
        relative_path, _ = get_relative_and_absolute_paths(
            nb_to_tmp_mapping[notebook].file
        )
        nb_to_tmp_mapping[notebook] = nb_to_tmp_mapping[notebook]._replace(
            file=relative_path
        )
    return nb_to_tmp_mapping


def _print_failed_notebook_errors(failed_notebooks: Mapping[str, str]) -> None:
    """Print exceptions from failed notebooks."""
    sys.stderr.write("\n")
    for failure, exp_repr in failed_notebooks.items():
        sys.stderr.write(BASE_ERROR_MESSAGE.format(notebook=failure, exp=exp_repr))
    sys.stderr.write(
        f"{BOLD}\n"
        "If you believe the notebook(s) to be valid, please "
        f"report a bug at https://github.com/nbQA-dev/nbQA/issues {RESET}\n"
    )
    sys.stderr.write("\n")


def _is_non_python_notebook(notebook: MutableMapping[str, Any]) -> bool:
    """
    If notebook is marked as non-Python, don't format it.

    All notebook metadata fields are optional, see
    https://nbformat.readthedocs.io/en/latest/format_description.html. So
    if a notebook has empty metadata, we will try to parse it anyway.
    """
    language = notebook.get("metadata", {}).get("language_info", {}).get("name", None)
    return language is not None and language.rstrip(string.digits) != "python"


def _save_code_sources(  # pylint: disable=too-many-locals
    nb_to_py_mapping: dict[str, TemporaryFile],
    process_cells: Sequence[str],
    skip_celltags: Sequence[str],
    dont_skip_bad_cells: bool,
    command: str,
) -> tuple[SavedSources, tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]]:
    """
    Save sources of notebooks.

    Record which notebooks fail to process, and which ones are non-Python ones.
    """
    failed_notebooks = {}
    non_python_notebooks = set()
    nb_info_mapping: MutableMapping[str, NotebookInfo] = {}

    first_passes: dict[
        str, tuple[Mapping[int, Sequence[MagicHandler]], set[int], str]
    ] = {}
    for notebook, (file_descriptor, file_name) in nb_to_py_mapping.items():
        try:
            notebook_json, _ = read_notebook(notebook)
            if notebook_json is None or _is_non_python_notebook(notebook_json):
                non_python_notebooks.add(notebook)
                continue
            temporary_lines, code_cells_to_ignore = save_code_source.pre_main(
                notebook_json,
                file_descriptor,
                process_cells,
                command,
                skip_celltags,
                dont_skip_bad_cells=dont_skip_bad_cells,
            )
            first_passes[notebook] = (temporary_lines, code_cells_to_ignore, file_name)
        except Exception as exp_repr:  # pylint: disable=W0703
            failed_notebooks[notebook] = repr(exp_repr)

    args = [nb_to_py_mapping[key].file for key in first_passes]
    newlinesbefore, newlinesafter = _fixup_newlines(
        args, first_passes, nb_to_py_mapping
    )
    for notebook, (
        temporary_lines,
        code_cells_to_ignore,
        file_name,
    ) in first_passes.items():
        notebook_json, _ = read_notebook(notebook)
        assert notebook_json is not None
        with open(file_name, encoding="utf-8") as fd:
            content = fd.read()
        parsed_cells = [CODE_SEPARATOR + i for i in content.split(CODE_SEPARATOR)]
        nb_info_mapping[notebook] = save_code_source.main(
            notebook_json,
            file_name,
            process_cells,
            skip_celltags,
            parsed_cells=parsed_cells[1:],
            temporary_lines=temporary_lines,
            code_cells_to_ignore=code_cells_to_ignore,
        )

    return SavedSources(nb_info_mapping, failed_notebooks, non_python_notebooks), (
        newlinesbefore,
        newlinesafter,
    )


def _save_markdown_sources(
    nb_to_md_mapping: dict[str, TemporaryFile],
    process_cells: Sequence[str],  # pylint: disable=W0613
    skip_celltags: Sequence[str],
    dont_skip_bad_cells: bool,  # pylint: disable=W0613
    command: str,  # pylint: disable=W0613
) -> tuple[SavedSources, tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]]:
    """
    Save markdown sources of notebooks.

    Record which notebooks fail to process.
    """
    failed_notebooks = {}
    non_python_notebooks = set()
    nb_info_mapping: MutableMapping[str, NotebookInfo] = {}

    for notebook, (file_descriptor, _) in nb_to_md_mapping.items():
        try:
            notebook_json, _ = read_notebook(notebook)
            if notebook_json is None or _is_non_python_notebook(notebook_json):
                non_python_notebooks.add(notebook)
                continue
            nb_info_mapping[notebook] = save_markdown_source.main(
                notebook_json,
                file_descriptor,
                skip_celltags,
            )
        except Exception as exp_repr:  # pylint: disable=W0703
            failed_notebooks[notebook] = repr(exp_repr)
    # we don't run autopep8 on md files, so this is just for compatibility
    _placeholder: dict[str, dict[str, int]] = {
        value.file: {} for key, value in nb_to_md_mapping.items()
    }
    return SavedSources(nb_info_mapping, failed_notebooks, non_python_notebooks), (
        _placeholder,
        _placeholder,
    )


SAVE_SOURCES = {False: _save_code_sources, True: _save_markdown_sources}


def _post_process_notebooks(  # pylint: disable=R0913
    saved_sources: SavedSources,
    nb_to_py_mapping: Mapping[str, TemporaryFile],
    mutated: bool,
    diff: bool,
    command: str,
    output: Output,
    newlinesbefore: dict[str, dict[str, int]],
    newlinesafter: dict[str, dict[str, int]],
    *,
    md: bool,
) -> tuple[bool, Output]:
    """Replace source in notebooks, modify output so it refers to notebooks."""
    actually_mutated = False
    for notebook, (_, temp_python_file) in nb_to_py_mapping.items():
        if (
            notebook in saved_sources.failed_notebooks
            or notebook in saved_sources.non_python_notebooks
        ):
            continue
        output = _replace_temp_python_file_references_in_out_err(
            temp_python_file, notebook, output.out, output.err, md=md
        )
        output = map_python_line_to_nb_lines(
            command,
            output.out,
            output.err,
            notebook,
            saved_sources.nb_info_mapping[notebook].cell_mappings,
        )

        if mutated:
            try:
                actually_mutated = (
                    REPLACE_FUNCTION[diff](
                        temp_python_file,
                        notebook,
                        saved_sources.nb_info_mapping[notebook],
                        newlinesbefore=newlinesbefore,
                        newlinesafter=newlinesafter,
                        md=md,
                    )
                    or actually_mutated
                )
            except Exception as exp_repr:  # pylint: disable=W0703
                saved_sources.failed_notebooks[notebook] = repr(exp_repr)
    return actually_mutated, output


def _main(cli_args: CLIArgs, configs: Configs) -> int:
    """
    Run third-party tool on a single notebook or directory.

    Parameters
    ----------
    cli_args
        Commandline arguments passed to nbqa.
    configs
        Configuration passed to nbqa from commandline or via a config file

    Returns
    -------
    int
        Output code from third-party tool.
    """
    try:
        nb_to_tmp_mapping = _get_nb_to_tmp_mapping(
            cli_args.root_dirs, configs["files"], configs["exclude"], configs["md"]
        )
    except FileNotFoundError as exc:
        sys.stderr.write(str(exc))
        return 1
    try:  # pylint disable=R0912
        if not nb_to_tmp_mapping:
            sys.stderr.write("No notebooks found in given path(s)\n")
            return 0
        saved_sources, (newlinesbefore, newlinesafter) = SAVE_SOURCES[configs["md"]](
            nb_to_tmp_mapping,
            configs["process_cells"],
            configs["skip_celltags"],
            configs["dont_skip_bad_cells"],
            cli_args.command,
        )
        if len(saved_sources.non_python_notebooks) == len(nb_to_tmp_mapping):
            sys.stderr.write("No valid Python notebooks found in given path(s)\n")
            return 0

        output, output_code, mutated = _run_command(
            cli_args.command,
            configs["addopts"],
            [
                i.file
                for key, i in nb_to_tmp_mapping.items()
                if key
                not in (
                    *saved_sources.failed_notebooks,
                    *saved_sources.non_python_notebooks,
                )
            ],
            shell=configs["shell"],
        )

        actually_mutated, output = _post_process_notebooks(
            saved_sources,
            nb_to_tmp_mapping,
            mutated,
            configs["diff"],
            cli_args.command,
            output,
            md=configs["md"],
            newlinesbefore=newlinesbefore,
            newlinesafter=newlinesafter,
        )

        sys.stdout.write(output.out)
        sys.stderr.write(output.err)

        if mutated and not actually_mutated:
            output_code = 0
            mutated = False

        if saved_sources.failed_notebooks:
            output_code = 123
            _print_failed_notebook_errors(saved_sources.failed_notebooks)

        if configs["diff"]:
            if mutated:
                sys.stdout.write(
                    "To apply these changes, remove the `--nbqa-diff` flag\n"
                )
            else:
                sys.stdout.write("Notebook(s) would be left unchanged\n")
            # For diff, we return 0 if no mutation would've occurred, and 1 otherwise.
            return int(mutated)

    finally:
        _clean_up_tmp_files(nb_to_tmp_mapping)
    return output_code


def _check_command_is_installed(command: str, *, shell: bool) -> None:
    """
    Check whether third-party tool is installed.

    Parameters
    ----------
    command
        Third-party tool being run on notebook(s).
    shell
        Whether the command should run in a shell instead of `python -m`.

    Raises
    ------
    ModuleNotFoundError
        If third-party tool isn't installed.
    UnsupportedPackageVersionError
        If third-party tool is of an unsupported version.
    CommandNotFoundError
        If third-party tool isn't available as a script in $PATH.
    """
    main_command, *_ = command.split()
    if shell:
        if which(main_command):
            return
        raise CommandNotFoundError(main_command)

    python_module = COMMAND_TO_PYTHON_MODULE.get(main_command, main_command)
    try:
        command_version = metadata.version(python_module)
    except metadata.PackageNotFoundError:
        try:
            import_module(python_module)
        except ImportError:
            if not os.path.isdir(python_module) and not os.path.isfile(
                f"{os.path.join(*python_module.split('.'))}.py"
            ):  # pragma: nocover(py<37)
                # I presume the lack of coverage in Python3.6 here is a bug, as all
                # these branches are actually covered.
                raise ModuleNotFoundError(
                    _get_command_not_found_msg(main_command)
                ) from None
    else:
        if main_command in MIN_VERSIONS:
            min_version = MIN_VERSIONS[main_command]
            if parse_version(command_version) < parse_version(min_version):
                raise UnsupportedPackageVersionError(
                    main_command, command_version, min_version
                )


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run third-party tool (e.g. :code:`mypy`) against notebook or directory.

    Parameters
    ----------
    argv
        Command-line arguments (if calling this function directly), defaults to
        :code:`None` if calling via command-line.
    """
    cli_args: CLIArgs = CLIArgs.parse_args(argv)
    project_root: Path = find_project_root(tuple(cli_args.root_dirs))
    configs: Configs = _get_configs(cli_args, project_root)
    _check_command_is_installed(cli_args.command, shell=configs["shell"])

    return _main(cli_args, configs)


if __name__ == "__main__":
    sys.exit(main())
