"""Parse nbqa configuration from one of the supported configuration files."""

from configparser import ConfigParser
from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple

from nbqa.cmdline import CLIArgs
from nbqa.config.config import CONFIG_SECTIONS, Configs
from nbqa.toml_parser import parse_from_pyproject_toml


def _parse_nbqa_ini_config(command: str, file_path: Path) -> Optional[Configs]:
    """
    Parse configuration from .nbqa.ini file.

    Parameters
    ----------
    command : str
        Third party tool to run
    file_path : Path
        Configuration file path

    Returns
    -------
    Optional[Configs]
        Config object parsed from the configuration file(if present)
    """
    config_parser = ConfigParser()
    config_parser.read(file_path)

    config: Configs = Configs()
    section: str = command

    for option in config_parser.options(section):
        config.set_config(option, config_parser.get(section, option, fallback=None))

    return config


def _parse_setupcfg_or_toxini_config(
    command: str, file_path: Path
) -> Optional[Configs]:
    """
    Parse nbqa configuration from setup.cfg or tox.ini.

    Parameters
    ----------
    command : str
        Third party tool to run
    file_path : Path
        Configuration file path

    Returns
    -------
    Optional[Configs]
        Config object parsed from the configuration file(if present)
    """
    config_parser = ConfigParser()
    config_parser.read(file_path)

    config: Optional[Configs] = None
    option: str = command

    # Check if this file contains the nbqa configuration
    for section in CONFIG_SECTIONS:
        section_name = f"{CONFIG_PREFIX}{section}"
        if config_parser.has_section(section_name):
            config = Configs()
            break

    if config is not None:
        for section in CONFIG_SECTIONS:
            section_name = f"{CONFIG_PREFIX}{section}"

            # We might not find the setting for a particular tool in any of the sections
            if config_parser.has_option(section_name, option):
                config.set_config(
                    section, config_parser.get(section_name, option, fallback=None)
                )

    return config


_ConfigHandler = Callable[..., Optional[Configs]]

CONFIG_PREFIX: str = "nbqa."

_CONFIG_FILE_HANDLERS: Sequence[Tuple[str, Optional[_ConfigHandler]]] = [
    ("pyproject.toml", parse_from_pyproject_toml),
    ("setup.cfg", _parse_setupcfg_or_toxini_config),
    ("tox.ini", _parse_setupcfg_or_toxini_config),
    (".nbqa.ini", _parse_nbqa_ini_config),
]


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

    for config_file, config_handler in _CONFIG_FILE_HANDLERS:
        file_path: Path = project_root / config_file

        if file_path.is_file() and config_handler is not None:
            config = config_handler(cli_args.command, file_path)

        # we found the config. skip other files
        if config is not None:
            break

    return config
