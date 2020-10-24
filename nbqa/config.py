"""Module responsible for storing and handling nbqa configuration."""

from collections import defaultdict
from importlib import import_module
from shlex import split
from typing import Any, Callable, ClassVar, Dict, List, NamedTuple, Optional

from pkg_resources import parse_version

from nbqa.cmdline import CLIArgs


class _ConfigSections(NamedTuple):  # pylint: disable=R0903
    """Stores all the config section names."""

    ADDOPTS: str = "addopts"
    CONFIG: str = "config"
    IGNORE_CELLS: str = "ignore_cells"
    MUTATE: str = "mutate"


CONFIG_SECTIONS = _ConfigSections()

DEFAULT_CONFIGS = defaultdict(lambda: [])

try:
    isort_module = import_module("isort")
    version = parse_version(isort_module.__version__)  # type: ignore
    if version >= parse_version("5.3.0"):
        DEFAULT_CONFIGS["isort"] = ["--treat-comment-as-code", "# %%"]
except ImportError:
    pass


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
        CONFIG_SECTIONS.ADDOPTS: lambda arg: split(arg)
        if isinstance(arg, str)
        else arg,
        CONFIG_SECTIONS.CONFIG: str,
        CONFIG_SECTIONS.IGNORE_CELLS: lambda arg: arg.split(",")
        if isinstance(arg, str)
        else arg,
        CONFIG_SECTIONS.MUTATE: bool,
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

        config.set_config(
            CONFIG_SECTIONS.ADDOPTS,
            cli_args.nbqa_addopts + DEFAULT_CONFIGS[cli_args.command],
        )
        config.set_config(CONFIG_SECTIONS.CONFIG, cli_args.nbqa_config)
        config.set_config(CONFIG_SECTIONS.IGNORE_CELLS, cli_args.nbqa_ignore_cells)
        config.set_config(CONFIG_SECTIONS.MUTATE, cli_args.nbqa_mutate)

        return config
