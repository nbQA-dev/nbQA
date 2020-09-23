"""Parse nbqa configuration from TOML file."""
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from nbqa.config import CONFIG_SECTIONS, Configs

_ROOT_CONFIG_KEY: str = "tool"
_NBQA_CONFIG_KEY: str = "nbqa"

_ConfigHandler = Callable[..., Optional[Configs]]
parse_from_pyproject_toml: Optional[_ConfigHandler] = None

try:
    import toml

    def _parse_config_from_toml(command: str, file_path: Path) -> Optional[Configs]:
        """
        Parse nbqa configuration from TOML file.

        Parameters
        ----------
        command : str
            Third party tool to run
        config_sections : List[str]
            Configuration sections supported by nbqa e.g addopts, config, mutate
        file_path : Path
            Configuration file path

        Returns
        -------
        Optional[Configs]
            Config object parsed from the configuration file(if present)
        """
        config: Optional[Configs] = None
        toml_config: Mapping[str, Any] = toml.load(str(file_path))
        nbqa_toml_config: Optional[Mapping[str, Mapping[str, Any]]] = toml_config.get(
            _ROOT_CONFIG_KEY, {}
        ).get(_NBQA_CONFIG_KEY, None)

        if nbqa_toml_config is not None:
            config = Configs()

            for section in CONFIG_SECTIONS:
                if section in nbqa_toml_config:
                    config.set_config(
                        section, nbqa_toml_config[section].get(command, None)
                    )

        return config

    parse_from_pyproject_toml = _parse_config_from_toml
except ImportError:  # pragma: nocover
    pass
