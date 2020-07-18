import subprocess


def test_flake8_return_code():
    output = subprocess.run(
        [
            "python",
            "-m",
            "nbqa",
            "--command",
            "flake8",
            "tests/data/notebook_for_testing.ipynb",
        ]
    )
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(
        [
            "python",
            "-m",
            "nbqa",
            "--command",
            "flake8",
            "tests/data/clean_notebook.ipynb",
        ]
    )
    result = output.returncode
    expected = 0
    assert result == expected


def test_black_return_code():
    output = subprocess.run(
        [
            "python",
            "-m",
            "nbqa",
            "black",
            "tests/data/notebook_for_testing.ipynb",
            "--check",
        ]
    )
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(
        [
            "python",
            "-m",
            "nbqa",
            "-c",
            "black",
            "--check",
            "tests/data/clean_notebook.ipynb",
        ]
    )
    result = output.returncode
    expected = 0
    assert result == expected

    output = subprocess.run(["python", "-m", "nbqa", "--command", "black", "--check"])
    result = output.returncode
    expected = 1
    assert result == expected

    output = subprocess.run(
        [
            "python",
            "-m",
            "nbqa",
            "--command",
            "black",
            "tests/data/clean_notebook.ipynb",
            "--check",
            "-l",
            "1",
        ]
    )
    result = output.returncode
    expected = 1
    assert result == expected
