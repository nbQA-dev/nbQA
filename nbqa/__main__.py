import argparse
import configparser
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

from nbqa import (
    __version__,
    put_magics_back_in,
    replace_magics,
    replace_source,
    save_source,
)


def _parse_args(raw_args):
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Adapter to run any code-quality tool on a Jupyter notebook.",
        usage=(
            "nbqa <command> <notebook or directory> <flags>\n"
            "e.g. `nbqa flake8 my_notebook.ipynb --ignore=E203`"
        ),
    )
    parser.add_argument("command", help="Command to run, e.g. `flake8`.")
    parser.add_argument("root_dir", help="Notebook or directory to run command on.")
    parser.add_argument("--version", action="version", version=f"nbQA {__version__}")
    try:
        args, kwargs = parser.parse_known_args(raw_args)
    except SystemExit as e:
        msg = (
            "Please specify both a command and a notebook/directory, e.g.\n"
            "nbqa flake8 my_notebook.ipynb"
        )
        raise ValueError(msg) from e
    command = args.command
    root_dir = args.root_dir
    return command, root_dir, kwargs


def _get_notebooks(root_dir) -> List[Path]:
    """
    Get generator with all notebooks in directory.
    """
    if not Path(root_dir).is_dir():
        return (i for i in (Path(root_dir),))
    return (i for i in Path(".").rglob("*.ipynb") if ".ipynb_checkpoints" not in str(i))


def _temp_python_file_for_notebook(notebook, tmpdir):
    """
    Get temporary file to save converted notebook into.
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


def _replace_full_path_out_err(out, err, temp_python_file, notebook):
    """
    Take care of case when out/err display full path.
    """
    out = out.replace(str(temp_python_file), str(notebook.resolve()))
    err = err.replace(str(temp_python_file), str(notebook.resolve()))

    # This next part is necessary to handle cases when `resolve` changes the path.
    # I couldn't reproduce this locally, but during CI, on the Windows job, I found
    # that VSSADM~1 was changing into VssAdministrator.
    out = out.replace(str(temp_python_file.resolve()), str(notebook.resolve()))
    err = err.replace(str(temp_python_file.resolve()), str(notebook.resolve()))
    return out, err


def _replace_relative_path_out_err(out, err, notebook):
    """
    Take care of case when out/err display relative path.

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


def _map_python_line_to_nb_lines(out, err, temp_python_file, notebook):
    """
    Make sure stdout and stderr make reference to Jupyter Notebook lines.
    """
    with open(str(temp_python_file), "r") as handle:
        cells = handle.readlines()
    mapping = {}
    cell_no = 0
    cell_count = None
    for n, i in enumerate(cells):
        if i == "# %%\n":
            cell_no += 1
            cell_count = 0
        else:
            cell_count += 1
        mapping[n + 1] = f"cell_{cell_no}:{cell_count}"
    out = re.sub(
        rf"(?<={notebook.name}:)\d+", lambda x: str(mapping[int(x.group())]), out,
    )
    err = re.sub(
        rf"(?<={notebook.name}:)\d+", lambda x: str(mapping[int(x.group())]), err,
    )
    return out, err


def _replace_temp_python_file_references_in_out_err(
    temp_python_file, notebook, out, err
):
    """
    Replace references to temporary directory name with current working directory.
    """
    out, err = _replace_full_path_out_err(out, err, temp_python_file, notebook)
    out, err = _replace_relative_path_out_err(out, err, notebook)
    out, err = _map_python_line_to_nb_lines(out, err, temp_python_file, notebook)
    return out, err


def _replace_tmpdir_references(out, err, tmpdirname, cwd=None):
    """
    Replace references to temporary directory name with current working directory.

    Examples
    --------
    >>> out = f"rootdir: {os.path.join('tmp', 'tmpdir')}\\n"
    >>> err = ""
    >>> tmpdirname = os.path.join('tmp', 'tmpdir')
    >>> cwd = Path("nbQA-dev")
    >>> out, err = _replace_tmpdir_references(out, err, tmpdirname, cwd)
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


def _create_blank_init_files(notebook, tmpdirname):
    """
    Replicate local (possibly blank) __init__ files to temporary directory.
    """
    parts = notebook.resolve().relative_to(Path.cwd()).parts
    init_files = Path(parts[0]).rglob("__init__.py")
    for i in init_files:
        Path(tmpdirname).joinpath(i).parent.mkdir(parents=True, exist_ok=True)
        Path(tmpdirname).joinpath(i).touch()


def _ensure_cell_separators_remain(temp_python_file):
    """
    Isort removes a blank line which separates the cells.
    """
    with open(str(temp_python_file), "r") as handle:
        py_file = handle.read()
    py_file = re.sub(r"(?<=\n\n)(?<!\n\n\n)# %%", "\n# %%", py_file)
    with open(str(temp_python_file), "w") as handle:
        handle.write(py_file)


def _get_arg(root_dir, tmpdirname, nb_to_py_mapping):
    """
    Get argument to run command against.

    If running against a single notebook, it'll be the filepath of the converted
    notebook in the temporary directory.
    If running against a directory, it'll be the directory mirrored in the temporary
    directory.

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


def _run_command(command, root_dir, tmpdirname, nb_to_py_mapping, kwargs):
    """
    Run third-party tool against given file or directory.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    arg = _get_arg(root_dir, tmpdirname, nb_to_py_mapping)

    try:
        output = subprocess.run(
            [command, str(arg), *kwargs],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=tmpdirname,
            env=env,
        )
    except FileNotFoundError as fnfe:
        raise ValueError(
            f"Command `{command}` not found. "
            "Please make sure you have it installed before running nbQA on it."
        ) from fnfe
    output_code = output.returncode

    out = output.stdout.decode()
    err = output.stderr.decode()
    return out, err, output_code


def main(raw_args=None):

    command, root_dir, kwargs = _parse_args(raw_args)

    notebooks = _get_notebooks(root_dir)

    with tempfile.TemporaryDirectory() as tmpdirname:

        nb_to_py_mapping = {
            notebook: _temp_python_file_for_notebook(notebook, tmpdirname)
            for notebook in notebooks
        }

        for notebook, temp_python_file in nb_to_py_mapping.items():
            save_source.main(notebook, temp_python_file)
            replace_magics.main(temp_python_file)
            _create_blank_init_files(notebook, tmpdirname)

        config = configparser.ConfigParser(allow_no_value=True)
        config.read(".nbqa.ini")
        if command in config.sections():
            configs = [
                [f"--{key}", val] if val is not None else [f"--{key}"]
                for key, val in config[command].items()
            ]
            kwargs.extend([j for i in configs for j in i])
        out, err, output_code = _run_command(
            command, root_dir, tmpdirname, nb_to_py_mapping, kwargs
        )

        out, err = _replace_tmpdir_references(out, err, tmpdirname)

        for notebook, temp_python_file in nb_to_py_mapping.items():
            out, err = _replace_temp_python_file_references_in_out_err(
                temp_python_file, notebook, out, err
            )

            put_magics_back_in.main(temp_python_file)
            _ensure_cell_separators_remain(temp_python_file)
            replace_source.main(temp_python_file, notebook)

        sys.stdout.write(out)
        sys.stderr.write(err)

    sys.exit(output_code)


if __name__ == "__main__":
    main()
