import os
import tempfile


def main(path):

    _, filename = tempfile.mkstemp(suffix=".py")

    os.system(f"ipynb-py-convert {path} {filename}")

    return filename
