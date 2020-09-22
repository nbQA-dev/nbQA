"""Module responsible for storing and handling nbqa configuration."""

from shlex import split
from typing import Any, Callable, ClassVar, Dict, List, Optional

from nbqa.cmdline import CLIArgs


class ConfigSections:  # pylint: disable=too-few-public-methods
    """Stores all the config section names."""

    ADDOPTS: ClassVar[str] = "addopts"
    CONFIG: ClassVar[str] = "config"
    IGNORE_CELLS: ClassVar[str] = "ignore_cells"
    MUTATE: ClassVar[str] = "mutate"

    @staticmethod
    def sections() -> List[str]:
        """
        Return an iterable of all configuration sections.

        Returns
        -------
        Iterable[str]
            Iterable of config section names
        """
        return [
            getattr(ConfigSections, section)
            for section in ConfigSections.__annotations__.keys()  # pylint: disable=no-member
        ]


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
    """

    _config_section_parsers: ClassVar[Dict[str, Callable]] = {
        ConfigSections.ADDOPTS: lambda arg: split(arg) if isinstance(arg, str) else arg,
        ConfigSections.CONFIG: str,
        ConfigSections.IGNORE_CELLS: lambda arg: arg.split(",")
        if isinstance(arg, str)
        else arg,
        ConfigSections.MUTATE: bool,
    }

    _mutate: bool = False
    _config: Optional[str] = None
    _ignore_cells: List[str] = []
    _addopts: List[str] = []

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

    def merge(self, other: "Configs") -> "Configs":
        """
        Merge another Config instance with this instance.

        Returns
        -------
        Configs
            Merged configuration object
        """
        self._addopts.extend(other.nbqa_addopts)
        self._config = self._config or other.nbqa_config
        self._ignore_cells = self._ignore_cells or other.nbqa_ignore_cells
        self._mutate = self._mutate or other.nbqa_mutate
        return self

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

        config.set_config(ConfigSections.ADDOPTS, cli_args.nbqa_addopts)
        config.set_config(ConfigSections.CONFIG, cli_args.nbqa_config)
        config.set_config(ConfigSections.IGNORE_CELLS, cli_args.nbqa_ignore_cells)
        config.set_config(ConfigSections.MUTATE, cli_args.nbqa_mutate)

        return config
