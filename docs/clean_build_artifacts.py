"""Cross platform way to call 'rm -rf docs/_build/ docs/api/' """
from pathlib import Path
from shutil import rmtree


def delete_artifacts() -> None:
    """Delete API and _build directories"""
    current_dir = Path(__file__).parent
    rmtree(current_dir / "api", ignore_errors=True)
    rmtree(current_dir / "_build", ignore_errors=True)


if __name__ == "__main__":
    delete_artifacts()
