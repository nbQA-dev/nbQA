import subprocess


def test_version() -> None:
    output = subprocess.run(["python", "-m", "nbqa", "--version"])
    assert output.returncode == 0
