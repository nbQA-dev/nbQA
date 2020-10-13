"""Check you can run :code:`nbqa --version`."""

import subprocess
from subprocess import PIPE

from nbqa import __version__


def test_version() -> None:
    """Check you can run :code:`nbqa --version`."""
    output = subprocess.run(
        ["nbqa", "--version"], stdout=PIPE, stderr=PIPE, universal_newlines=True
    )
    assert output.stdout.strip() == f"nbqa {__version__}"
    assert output.returncode == 0
