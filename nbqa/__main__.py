import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

from nbqa import put_magics_back_in, replace_magics, replace_source, save_source


def _parse_args(raw_args):
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("command")
    parser.add_argument("root_dir", default=".", nargs="?")
    args, kwargs = parser.parse_known_args(raw_args)
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
    temp_python_file = Path(tmpdir).joinpath(notebook).with_suffix(".py")
    temp_python_file.parent.mkdir(parents=True, exist_ok=True)
    return temp_python_file


def _replace_temp_python_file_references_in_out_err(
    temp_python_file, notebook, out, err
):
    """
    Out and err refer to temporary Python files - make them refer to Jupyter notebooks.

    Needs docstring with example, gotta doctest it.
    """
    # Take care of case when out/err display full path
    out = out.replace(str(temp_python_file), notebook.name)
    err = err.replace(str(temp_python_file), notebook.name)

    # Take care of case when out/err display relative path
    out = out.replace(str(notebook.with_suffix(".py")), str(notebook))
    err = err.replace(str(notebook.with_suffix(".py")), str(notebook))

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
    return out, err


def _replace_tmpdir_references(out, err, tmpdirname):
    out = re.sub(rf"{tmpdirname}(?=\s)", str(Path.cwd()), out)
    err = re.sub(rf"{tmpdirname}(?=\s)", str(Path.cwd()), err)
    return out, err


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

        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        output = subprocess.run(
            [command, tmpdirname, *kwargs],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=tmpdirname,
            env=env,
        )
        output_code = output.returncode

        out = output.stdout.decode()
        err = output.stderr.decode()

        out, err = _replace_tmpdir_references(out, err, tmpdirname)

        for notebook, temp_python_file in nb_to_py_mapping.items():
            out, err = _replace_temp_python_file_references_in_out_err(
                temp_python_file, notebook, out, err
            )

            put_magics_back_in.main(temp_python_file)

            replace_source.main(temp_python_file, notebook)

        sys.stdout.write(out)
        sys.stderr.write(err)

    sys.exit(output_code)


if __name__ == "__main__":
    main()
