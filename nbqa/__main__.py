import os
from pathlib import Path

import typer

from nbqa import put_magics_back_in, replace_magics


def main(command, dir="."):
    notebooks = Path(".").rglob("*.ipynb")
    for notebook in notebooks:
        os.system(f"nbstripout {notebook}")
        python_file = Path(f"{Path(notebook).stem}.py")
        assert not python_file.exists()
        os.system(f"ipynb-py-convert {notebook} {str(python_file)}")
        replace_magics.main(python_file)
        os.system(f"{command} {python_file}")
        put_magics_back_in.main(python_file)
        Path(notebook).unlink()
        os.system(f"ipynb-py-convert {python_file} {notebook}")
        python_file.unlink()


if __name__ == "__main__":
    typer.run(main)
