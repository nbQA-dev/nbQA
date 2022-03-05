"""Check you can run :code:`nbqa --version`."""

import subprocess

from nbqa import __version__


def test_version() -> None:
    """Check you can run :code:`nbqa --version`."""
    output = subprocess.run(["nbqa", "--version"], capture_output=True, text=True)
    assert output.stdout.strip() == f"nbqa {__version__}"
    assert output.returncode == 0
