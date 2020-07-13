import re
import subprocess
import sys
from pathlib import Path

from nbqa import put_magics_back_in, replace_magics, replace_source, save_source


def main(args=None):

    import argparse

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("command")
    parser.add_argument("root_dir", default=".", nargs="?")
    args, kwargs = parser.parse_known_args(args)
    command = args.command
    root_dir = args.root_dir

    if not Path(root_dir).is_dir():
        notebooks = [Path(root_dir)]
    else:
        notebooks = Path(root_dir).rglob("*.ipynb")
    output_code = 0
    for notebook in notebooks:
        if "ipynb_checkpoints" in str(notebook):
            continue

        tempfile = save_source.main(notebook)
        replace_magics.main(tempfile)

        try:
            output = subprocess.run(
                [command, tempfile, *kwargs],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            if output_code == 0:
                output_code = output.returncode
        except subprocess.CalledProcessError as e:
            output_code = e.returncode
            output = e.output

        # replace ending, convert to str
        out = output.stdout.decode().replace(tempfile, notebook.name)
        err = output.stderr.decode().replace(tempfile, notebook.name)

        with open(tempfile, "r") as handle:
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

        put_magics_back_in.main(tempfile)

        replace_source.main(tempfile, notebook)

    sys.exit(output_code)


if __name__ == "__main__":
    main()
