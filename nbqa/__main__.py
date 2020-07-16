import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator
import tempfile

from nbqa import put_magics_back_in, replace_magics, replace_source, save_source

import argparse


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


def _get_notebooks(root_dir) -> Iterator[Path]:
    """
    Get generator with all notebooks in directory.
    """
    if not Path(root_dir).is_dir():
        return (i for i in (Path(root_dir),))
    return Path(root_dir).rglob("*.ipynb")

def main(raw_args=None):
    
    command, root_dir, kwargs = _parse_args(raw_args)

    notebooks = _get_notebooks(root_dir)

    output_code = 0

    with tempfile.TemporaryDirectory() as tmpdirname:

        for notebook in notebooks:
            if "ipynb_checkpoints" in str(notebook):
                continue

            temp_file = save_source.main(notebook, tmpdirname)  # let's pass the temp dir to here
            replace_magics.main(temp_file)

            output = subprocess.run(
                [command, str(temp_file), *kwargs],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            if output_code == 0:
                output_code = output.returncode

            # replace ending, convert to str
            out = output.stdout.decode().replace(str(temp_file), notebook.name)
            err = output.stderr.decode().replace(str(temp_file), notebook.name)

            with open(str(temp_file), "r") as handle:
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

            sys.stdout.write(out)
            sys.stderr.write(err)

            put_magics_back_in.main(temp_file)

            replace_source.main(temp_file, notebook)

    sys.exit(output_code)


if __name__ == "__main__":
    main()
