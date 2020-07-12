import os
from pathlib import Path

import typer

from nbqa import put_magics_back_in, replace_magics, replace_source, save_source


def main(command, dir="."):
    notebooks = Path(".").rglob("*.ipynb")
    for notebook in notebooks:
        if "ipynb_checkpoints" in str(notebook):
            continue
        python_file = Path(f"{Path(notebook).stem}.py")
        assert not python_file.exists()
        save_source.main(notebook, python_file)

        replace_magics.main(python_file)
        os.system(f"{command} {python_file}")
        put_magics_back_in.main(python_file)

        replace_source.main(python_file, notebook)

        python_file.unlink()


if __name__ == "__main__":
    typer.run(main)
