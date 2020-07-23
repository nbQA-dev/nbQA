"""
Check you can run :code:`nbqa --version`.
"""

import subprocess


def test_version() -> None:
    """
    Check you can run :code:`nbqa --version`.
    """
    output = subprocess.run(["python", "-m", "nbqa", "--version"])
    assert output.returncode == 0
