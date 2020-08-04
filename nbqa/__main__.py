"""Run third-party tool (e.g. :code:`mypy`) against notebook or directory."""

import argparse
import configparser
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from textwrap import dedent
from typing import Dict, Iterator, List, Optional, Set, Tuple

from nbqa import (
    __version__,
    put_magics_back_in,
    replace_magics,
    replace_source,
    save_source,
)


def _parse_args(raw_args: Optional[List[str]]) -> Tuple[argparse.Namespace, List[str]]:
    """
    Parse command-line arguments.

    Parameters
    ----------
    raw_args
        Passed via command-line.

    Returns
    -------
    command
        The third-party tool to run (e.g. :code:`mypy`).
    root_dirs
        The notebooks or directories to run third-party tool on.
    allow_mutation
        Whether to allow 3rd party tools to modify notebooks.
    nbqa_config
        Config file for 3rd party tool (e.g. :code:`.mypy.ini`)
    kwargs
        Any additional flags passed to third-party tool (e.g. :code:`--quiet`).

    Raises
    ------
    ValueError
        If user doesn't specify both a command and a notebook/directory to run it
        on (e.g. if the user runs :code:`nbqa flake8` instead of :code:`nbqa flake8 .`).
    """
    parser = argparse.ArgumentParser(
        description="Adapter to run any code-quality tool on a Jupyter notebook.",
        usage=dedent(
            """\
            nbqa <command> <notebook or directory> <flags>
            example:

                nbqa flake8 my_notebook.ipynb --ignore=E203\
            """
        ),
    )
    parser.add_argument("command", help="Command to run, e.g. `flake8`.")
    parser.add_argument(
        "root_dirs", nargs="+", help="Notebooks or directories to run command on."
    )
    parser.add_argument(
        "--nbqa-mutate", action="store_true", help="Allows `nbqa` to modify notebooks.",
    )
    parser.add_argument(
        "--nbqa-config",
        required=False,
        help="Config file for third-party tool (e.g. `setup.cfg`)",
    )
    parser.add_argument("--version", action="version", version=f"nbQA {__version__}")
    try:
        args, kwargs = parser.parse_known_args(raw_args)
    except SystemExit as exception:
        if exception.code != 0:
            msg = (
                "Please specify both a command and a notebook/directory, e.g.\n"
                "nbqa flake8 my_notebook.ipynb"
            )
            raise ValueError(msg) from exception
        sys.exit(0)  # pragma: nocover
    return args, kwargs


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


def _temp_python_file_for_notebook(notebook: Path, tmpdir: str) -> Path:
    """
    Get temporary file to save converted notebook into.

    Parameters
    ----------
    notebook
        Notebook that third-party tool will be run on.
    tmpdir
        Temporary directory where converted notebooks will be saved.

    Returns
    -------
    Path
        Temporary Python file whose location mirrors that of the notebook, but
        inside the temporary directory.
    """
    # Add 3 extra whitespaces because `ipynb` is 3 chars longer than `py`.
    temp_python_file = (
        Path(tmpdir)
        .joinpath(notebook.resolve().relative_to(Path.cwd()).parent)
        .joinpath(f"{notebook.stem}   ")
        .with_suffix(".py")
    )
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


def _replace_relative_path_out_err(
    out: str, err: str, notebook: Path
) -> Tuple[str, str]:
    """
    Replace references to temporary Python file's relative path with notebook's path.

    Parameters
    ----------
    out
        Captured stdout from third-party tool.
    err
        Captured stderr from third-party tool.
    notebook
        Original Jupyter notebook.

    Returns
    -------
    out
        Stdout with temporary Python file's relative path with notebook's path.
    err
        Stderr with temporary Python file's relative path with notebook's path.
    Examples
    --------
    >>> out = "notebook   .py ."
    >>> err = ""
    >>> notebook = Path('notebook.ipynb')
    >>> out, err = _replace_relative_path_out_err(out, err, notebook)
    >>> out
    'notebook.ipynb .'
    """
    out = out.replace(
        str(notebook.parent.joinpath(f"{notebook.stem}   ").with_suffix(".py")),
        str(notebook),
    )
    err = err.replace(
        str(notebook.parent.joinpath(f"{notebook.stem}   ").with_suffix(".py")),
        str(notebook),
    )
    return out, err


def _map_python_line_to_nb_lines(
    out: str, err: str, temp_python_file: Path, notebook: Path
) -> Tuple[str, str]:
    """
    Make sure stdout and stderr make reference to Jupyter Notebook cells and lines.

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
        Stdout with references to temporary Python file's lines replaced with references
        to notebook's cells and lines.
    err
        Stderr with references to temporary Python file's lines replaced with references
        to notebook's cells and lines.
    """
    with open(str(temp_python_file), "r") as handle:
        cells = handle.readlines()
    mapping = {}
    cell_no = 0
    cell_count = None
    for idx, cell in enumerate(cells):
        if cell == "# %%\n":
            cell_no += 1
            cell_count = 0
        else:
            assert cell_count is not None
            cell_count += 1
        mapping[idx + 1] = f"cell_{cell_no}:{cell_count}"
    out = re.sub(
        rf"(?<={notebook.name}:)\d+", lambda x: str(mapping[int(x.group())]), out,
    )
    err = re.sub(
        rf"(?<={notebook.name}:)\d+", lambda x: str(mapping[int(x.group())]), err,
    )
    return out, err


def _replace_temp_python_file_references_in_out_err(
    temp_python_file: Path, notebook: Path, out: str, err: str
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

    Returns
    -------
    out
        Stdout with temporary directory replaced by current working directory.
    err
        Stderr with temporary directory replaced by current working directory.
    """
    out, err = _replace_full_path_out_err(out, err, temp_python_file, notebook)
    out, err = _replace_relative_path_out_err(out, err, notebook)
    out, err = _map_python_line_to_nb_lines(out, err, temp_python_file, notebook)
    return out, err


def _replace_tmpdir_references(
    out: str, err: str, cwd: Optional[Path] = None
) -> Tuple[str, str]:
    r"""
    Replace references to temporary directory name with current working directory.

    Parameters
    ----------
    out
        Captured stdout from third-party tool.
    err
        Captured stderr from third-party tool.
    cwd
        Current working directory.

    Returns
    -------
    out
        Stdout with references to temporary Python replaced with references to notebook.
    err
        Stderr with references to temporary Python replaced with references to notebook.

    Examples
    --------
    >>> out = f"rootdir: {os.path.join('tmp', 'tmpdir')}\\n"
    >>> err = ""
    >>> cwd = Path("nbQA-dev")
    >>> out, err = _replace_tmpdir_references(out, err, cwd)
    >>> out.strip(os.linesep)
    'rootdir: nbQA-dev'
    """
    if cwd is None:
        cwd = Path.cwd().resolve()
    new_out = os.linesep.join(
        [
            i if not i.startswith("rootdir: ") else f"rootdir: {str(cwd)}"
            for i in out.splitlines()
        ]
    )
    new_err = os.linesep.join(
        [
            i if not i.startswith("rootdir: ") else f"rootdir: {str(cwd)}"
            for i in err.splitlines()
        ]
    )
    if new_out:
        new_out += os.linesep
    if new_err:
        new_err += os.linesep
    return new_out, new_err


def _create_blank_init_files(notebook: Path, tmpdirname: str) -> None:
    """
    Replicate local (possibly blank) __init__ files to temporary directory.

    Parameters
    ----------
    notebook
        Notebook third-party tool is being run against.
    tmpdirname
        Temporary directory to store converted notebooks in.
    """
    parts = notebook.resolve().relative_to(Path.cwd()).parts

    for idx in range(1, len(parts)):
        init_file = next(Path(os.path.join(*parts[:idx])).glob("__init__.py"))
        if init_file is not None:
            Path(tmpdirname).joinpath(init_file).parent.mkdir(
                parents=True, exist_ok=True
            )
            Path(tmpdirname).joinpath(init_file).touch()


def _preserve_config_files(nbqa_config: Optional[str], tmpdirname: str) -> None:
    """
    Copy local config file to temporary directory.

    Parameters
    ----------
    nbqa_config
        Config file for third-party tool (e.g. mypy).
    tmpdirname
        Temporary directory to store converted notebooks in.
    """
    if nbqa_config is None:
        return
    Path(tmpdirname).joinpath(
        Path(nbqa_config).resolve().relative_to(Path.cwd())
    ).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        str(nbqa_config),
        str(
            Path(tmpdirname).joinpath(
                Path(nbqa_config).resolve().relative_to(Path.cwd())
            )
        ),
    )


def _ensure_cell_separators_remain(temp_python_file: Path) -> None:
    """
    Reinstate blank line which separates the cells (may be removed by isort).

    Parameters
    ----------
    temp_python_file
        Temporary Python file notebook was converted to.
    """
    with open(str(temp_python_file), "r") as handle:
        py_file = handle.read()
    py_file = re.sub(r"(?<=\n\n)(?<!\n\n\n)# %%", "\n# %%", py_file)
    with open(str(temp_python_file), "w") as handle:
        handle.write(py_file)


def _get_arg(
    root_dir: str, tmpdirname: str, nb_to_py_mapping: Dict[Path, Path]
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
        arg = Path(tmpdirname).joinpath(root_dir)
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
    root_dir: str,
    tmpdirname: str,
    nb_to_py_mapping: Dict[Path, Path],
    kwargs: List[str],
) -> Tuple[str, str, int, bool]:
    """
    Run third-party tool against given file or directory.

    Parameters
    ----------
    command
        Third-party tool (e.g. :code:`mypy`) to run against notebook.
    root_dir
        Notebook or directory to run third-party tool on.
    tmpdirname
        Temporary directory where converted notebooks will be stored.
    nb_to_py_mapping
        Mapping between notebooks and Python files corresponding to converted notebooks.
    kwargs
        Flags to pass to third-party tool (e.g. :code:`--verbose`).

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

    arg = _get_arg(root_dir, tmpdirname, nb_to_py_mapping)

    if shutil.which(command) is None:
        raise ValueError(
            f"Command `{command}` not found. "
            "Please make sure you have it installed before running nbQA on it."
        )

    before = _get_mtimes(arg)

    output = subprocess.run(
        [command, str(arg), *kwargs],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=tmpdirname,
        env=env,
    )

    after = _get_mtimes(arg)
    mutated = after != before

    output_code = output.returncode

    out = output.stdout.decode()
    err = output.stderr.decode()
    return out, err, output_code, mutated


def _get_configs(
    args: argparse.Namespace, kwargs: List[str], tmpdirname: str,
) -> Tuple[bool, bool]:
    """
    Deal with extra configs for 3rd party tool.

    Parameters
    ----------
    args
        Arguments passed to nbqa
    kwargs
        Extra flags for third party tool
    tmpdirname
        Temporary directory where notebooks are copied to.

    Returns
    -------
    bool
        Whether or not to copy __init__.py to temporary directory.
    bool
        Whether to allow nbqa to modify notebooks.
    """
    config = configparser.ConfigParser()
    config.read(".nbqa.ini")
    nbqa_config = args.nbqa_config
    allow_mutation = args.nbqa_mutate
    if args.command in config.sections():
        addopts = config[args.command].get("addopts")
        if addopts is not None:
            kwargs.extend(config[args.command]["addopts"].split())
        if nbqa_config is None:
            nbqa_config = config[args.command].get("config")
        if not allow_mutation:
            allow_mutation = bool(config[args.command].get("mutate"))
    _preserve_config_files(nbqa_config, tmpdirname)
    return allow_mutation


def _run_on_one_root_dir(
    root_dir: str, args: argparse.Namespace, kwargs: List[str]
) -> int:
    """
    Run third-party tool on a single notebook or directory.

    Parameters
    ----------
    args
        Arguments passed to nbqa.
    kwargs
        Additional flags to pass to 3rd party tool

    Returns
    -------
    int
        Output code from third-party tool.
    """
    notebooks = _get_notebooks(root_dir)

    with tempfile.TemporaryDirectory() as tmpdirname:

        nb_to_py_mapping = {
            notebook: _temp_python_file_for_notebook(notebook, tmpdirname)
            for notebook in notebooks
        }

        allow_mutation = _get_configs(args, kwargs, tmpdirname)

        for notebook, temp_python_file in nb_to_py_mapping.items():
            save_source.main(notebook, temp_python_file)
            replace_magics.main(temp_python_file)
            _create_blank_init_files(notebook, tmpdirname)

        out, err, output_code, mutated = _run_command(
            args.command, root_dir, tmpdirname, nb_to_py_mapping, kwargs
        )

        out, err = _replace_tmpdir_references(out, err)

        for notebook, temp_python_file in nb_to_py_mapping.items():
            out, err = _replace_temp_python_file_references_in_out_err(
                temp_python_file, notebook, out, err
            )
            if mutated and not allow_mutation:
                if args.nbqa_config:
                    kwargs += [f"--nbqa-config={args.nbqa_config}"]
                kwargs += ["--nbqa-mutate"]
                raise SystemExit(
                    dedent(
                        f"""\
                        💥 Mutation detected, will not reformat! Please use the `--nbqa-mutate` flag:

                            nbqa {args.command} {root_dir} {' '.join(kwargs)}
                        """
                    )
                )
            if mutated:
                put_magics_back_in.main(temp_python_file)
                _ensure_cell_separators_remain(temp_python_file)
                replace_source.main(temp_python_file, notebook)

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
    args, kwargs = _parse_args(raw_args)

    output_codes = [_run_on_one_root_dir(i, args, kwargs) for i in args.root_dirs]

    sys.exit(int(any(output_codes)))


if __name__ == "__main__":
    main()
