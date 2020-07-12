import re
import subprocess
from pathlib import Path

import typer

from nbqa import put_magics_back_in, replace_magics, replace_source, save_source


def main(command, dir="."):
    notebooks = Path(".").rglob("*.ipynb")
    output_code = 0
    for notebook in notebooks:
        if "ipynb_checkpoints" in str(notebook):
            continue
        python_file = Path(f"{Path(notebook).stem}.py")
        assert not python_file.exists()
        save_source.main(notebook, python_file)

        replace_magics.main(python_file)

        try:
            output = subprocess.check_output(
                f"{command} {python_file}", shell=True, stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            output_code = e.returncode
            output = e.output
        breakpoint()

        # replace ending, convert to str
        output = output.decode().replace(".py", ".ipynb")

        with open("test_notebook.py", "r") as handle:
            data = handle.read()
        cells = data.split("\n")
        mapping = {}
        cell_no = 0
        cell_count = 0
        for n, i in enumerate(cells):
            if i == "# %%":
                cell_no += 1
                cell_count = 0
            else:
                cell_count += 1
                mapping[n + 1] = f"{cell_no}:{cell_count}"
        breakpoint()
        output = re.sub(
            r"(?<=test_notebook\.ipynb:)\d+",
            lambda x: "cell_" + str(mapping[int(x.group())]),
            output,
        )

        # replace line numbers
        print(output)

        put_magics_back_in.main(python_file)

        replace_source.main(python_file, notebook)

        python_file.unlink()

    return output_code


if __name__ == "__main__":
    typer.run(main)
