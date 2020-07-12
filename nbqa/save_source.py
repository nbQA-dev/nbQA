import subprocess
import tempfile


def main(path):

    _, filename = tempfile.mkstemp(suffix=".py")

    subprocess.run(["ipynb-py-convert", path, filename])

    return filename
