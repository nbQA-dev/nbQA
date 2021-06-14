"""Parse nbqa configuration from one of the supported configuration files."""

from pathlib import Path
from typing import Optional

from nbqa.cmdline import CLIArgs
from nbqa.config.config import Configs
from nbqa.toml_parser import parse_from_pyproject_toml

CONFIG_PREFIX: str = "nbqa."


def parse_config_from_file(cli_args: CLIArgs, project_root: Path) -> Optional[Configs]:
    """
    Find the file that contains nbqa configuration and parse the configuration from it.

    Parameters
    ----------
    cli_args : CLIArgs
        Commandline arguments passed to nbqa
    project_root : Path
        Root of the repository or project

    Returns
    -------
    Optional[Configs]
        Configuration read from the file(if any)
    """
    config: Optional[Configs] = None
    file_path: Path = project_root / "pyproject.toml"
    if file_path.is_file():
        config = parse_from_pyproject_toml(cli_args.command, file_path)
    return config
