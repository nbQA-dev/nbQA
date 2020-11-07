"""Module responsible for storing and handling nbqa configuration."""

from shlex import split
from typing import Any, Callable, ClassVar, Dict, List, Mapping, NamedTuple, Optional

import toml
from pkg_resources import resource_filename

from nbqa.cmdline import CLIArgs


class _ConfigSections(NamedTuple):  # pylint: disable=R0903
    """Stores all the config section names."""

    ADDOPTS: str = "addopts"
    CONFIG: str = "config"
    IGNORE_CELLS: str = "ignore_cells"
    MUTATE: str = "mutate"
    FILES: str = "files"
    EXCLUDE: str = "exclude"


CONFIG_SECTIONS = _ConfigSections()


DEFAULT_CONFIG: Mapping[str, Mapping] = toml.load(
    resource_filename("nbqa.config", "default_config.toml")
)


class Configs:
    """
    Nbqa configuration.

    Attributes
    ----------
    nbqa_mutate
        Whether to allow nbqa to modify notebooks.
    nbqa_config
        Configuration of the third party tool.
    nbqa_ignore_cells
        Extra cells which nbqa should ignore.
    nbqa_addopts
        Additional arguments passed to the third party tool
    nbqa_files
        Global file include pattern.
    nbqa_exclude
        Global file exclude pattern.
    """

    _config_section_parsers: ClassVar[Dict[str, Callable]] = {
        CONFIG_SECTIONS.ADDOPTS: lambda arg: split(arg)
        if isinstance(arg, str)
        else arg,
        CONFIG_SECTIONS.CONFIG: str,
        CONFIG_SECTIONS.IGNORE_CELLS: lambda arg: arg.split(",")
        if isinstance(arg, str)
        else arg,
        CONFIG_SECTIONS.MUTATE: bool,
        CONFIG_SECTIONS.FILES: str,
        CONFIG_SECTIONS.EXCLUDE: str,
    }

    _mutate: bool = False
    _config: Optional[str] = None
    _ignore_cells: List[str] = []
    _addopts: List[str] = []
    _files: Optional[str] = None
    _exclude: Optional[str] = None

    def set_config(self, config: str, value: Any) -> None:
        """
        Store value for the config.

        Parameters
        ----------
        config : str
            Config setting supported by nbqa
        value : Any
            Config value
        """
        if value:
            self.__setattr__(f"_{config}", self._config_section_parsers[config](value))

    @property
    def nbqa_mutate(self) -> bool:
        """Flag if nbqa is allowed to modify the original notebook(s)."""
        return self._mutate

    @property
    def nbqa_config(self) -> Optional[str]:
        """Return the configuration of the third party tool."""
        return self._config

    @property
    def nbqa_addopts(self) -> List[str]:
        """Additional options to be passed to the third party command to run."""
        return self._addopts

    @property
    def nbqa_ignore_cells(self) -> List[str]:
        """Additional cells which nbqa should ignore."""
        return self._ignore_cells

    @property
    def nbqa_files(self) -> Optional[str]:
        """Additional cells which nbqa should ignore."""
        return self._files

    @property
    def nbqa_exclude(self) -> Optional[str]:
        """Additional cells which nbqa should ignore."""
        return self._exclude

    def merge(self, other: "Configs") -> "Configs":
        """
        Merge another Config instance with this instance.

        Returns
        -------
        Configs
            Merged configuration object
        """
        config: Configs = Configs()

        config.set_config(CONFIG_SECTIONS.ADDOPTS, self._addopts + other.nbqa_addopts)
        config.set_config(CONFIG_SECTIONS.CONFIG, self._config or other.nbqa_config)
        config.set_config(
            CONFIG_SECTIONS.IGNORE_CELLS, self._ignore_cells or other.nbqa_ignore_cells
        )
        config.set_config(CONFIG_SECTIONS.MUTATE, self._mutate or other.nbqa_mutate)
        config.set_config(CONFIG_SECTIONS.FILES, self._files or other.nbqa_files)
        config.set_config(CONFIG_SECTIONS.EXCLUDE, self._exclude or other.nbqa_exclude)
        return config

    @staticmethod
    def parse_from_cli_args(cli_args: CLIArgs) -> "Configs":
        """
        Parse nbqa configuration from command line arguments.

        Returns
        -------
        Configs
            Configuration passed via command line arguments.
        """
        config: Configs = Configs()

        config.set_config(CONFIG_SECTIONS.ADDOPTS, cli_args.nbqa_addopts)
        config.set_config(CONFIG_SECTIONS.CONFIG, cli_args.nbqa_config)
        config.set_config(CONFIG_SECTIONS.IGNORE_CELLS, cli_args.nbqa_ignore_cells)
        config.set_config(CONFIG_SECTIONS.MUTATE, cli_args.nbqa_mutate)
        config.set_config(CONFIG_SECTIONS.FILES, cli_args.nbqa_files)
        config.set_config(CONFIG_SECTIONS.EXCLUDE, cli_args.nbqa_exclude)

        return config

    @staticmethod
    def get_default_config(command: str) -> "Configs":
        """Merge defaults."""
        defaults: Configs = Configs()
        defaults.set_config(
            CONFIG_SECTIONS.ADDOPTS, DEFAULT_CONFIG["addopts"].get(command)
        )
        defaults.set_config(
            CONFIG_SECTIONS.CONFIG, DEFAULT_CONFIG["config"].get(command)
        )
        defaults.set_config(
            CONFIG_SECTIONS.IGNORE_CELLS, DEFAULT_CONFIG["ignore_cells"].get(command)
        )
        defaults.set_config(
            CONFIG_SECTIONS.MUTATE, DEFAULT_CONFIG["mutate"].get(command)
        )
        defaults.set_config(CONFIG_SECTIONS.FILES, DEFAULT_CONFIG["files"].get(command))
        defaults.set_config(
            CONFIG_SECTIONS.EXCLUDE, DEFAULT_CONFIG["exclude"].get(command)
        )

        return defaults
