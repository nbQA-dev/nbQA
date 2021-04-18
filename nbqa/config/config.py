"""Module responsible for storing and handling nbqa configuration."""

import collections
from pathlib import Path
from shlex import split
from textwrap import dedent
from typing import Any, Callable, ClassVar, Dict, Mapping, Optional, Sequence, Union

import toml
from pkg_resources import resource_filename

from nbqa.cmdline import CLIArgs

ConfigParser = Callable[[str], Union[str, bool, Sequence[str]]]


class _ConfigSections(
    collections.namedtuple(
        "_ConfigSections",
        (
            "ADDOPTS",
            "CONFIG",
            "IGNORE_CELLS",
            "PROCESS_CELLS",
            "MUTATE",
            "DIFF",
            "FILES",
            "EXCLUDE",
        ),
    )
):
    """Config sections."""

    __slots__ = ()

    def __new__(  # pylint: disable=R0913
        cls,
        ADDOPTS: str = "addopts",
        CONFIG: str = "config",
        IGNORE_CELLS: str = "ignore_cells",
        PROCESS_CELLS: str = "process_cells",
        MUTATE: str = "mutate",
        DIFF: str = "diff",
        FILES: str = "files",
        EXCLUDE: str = "exclude",
    ) -> "_ConfigSections":
        """Python3.6.0 doesn't support defaults for namedtuples."""
        return super().__new__(
            cls,
            ADDOPTS,
            CONFIG,
            IGNORE_CELLS,
            PROCESS_CELLS,
            MUTATE,
            DIFF,
            FILES,
            EXCLUDE,
        )


CONFIG_SECTIONS = _ConfigSections()


DEFAULT_CONFIG: Mapping[str, Mapping[str, Sequence[str]]] = toml.load(
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
        Deprecated.
    nbqa_process_cells
        Process code within cells with these cell magics.
    nbqa_addopts
        Additional arguments passed to the third party tool
    nbqa_files
        Global file include pattern.
    nbqa_exclude
        Global file exclude pattern.
    """

    CONFIG_SECTION_PARSERS: ClassVar[Dict[str, ConfigParser]] = {}
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.ADDOPTS] = (
        lambda arg: split(arg) if isinstance(arg, str) else arg
    )
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.CONFIG] = str
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.IGNORE_CELLS] = (
        lambda arg: arg.split(",") if isinstance(arg, str) else arg
    )
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.PROCESS_CELLS] = (
        lambda arg: arg.split(",") if isinstance(arg, str) else arg
    )
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.MUTATE] = bool
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.DIFF] = bool
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.FILES] = str
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.EXCLUDE] = str

    _mutate: bool = False
    _config: Optional[str] = None
    _ignore_cells: Sequence[str] = []
    _process_cells: Sequence[str] = []
    _addopts: Sequence[str] = []
    _diff: bool = False
    _files: Optional[str] = None
    _exclude: Optional[str] = None

    def set_config(self, config: str, value: Any) -> None:
        """
        Store value for the config.

        Parameters
        ----------
        config
            Config setting supported by nbqa
        value
            Config value
        """
        if value:
            self.__setattr__(f"_{config}", self.CONFIG_SECTION_PARSERS[config](value))

    @property
    def nbqa_mutate(self) -> bool:
        """Flag if nbqa is allowed to modify the original notebook(s)."""
        return self._mutate

    @property
    def nbqa_diff(self) -> bool:
        """Show diff instead of replacing notebook code."""
        return self._diff

    @property
    def nbqa_config(self) -> Optional[str]:
        """Return the configuration of the third party tool."""
        return self._config

    @property
    def nbqa_addopts(self) -> Sequence[str]:
        """Additional options to be passed to the third party command to run."""
        return self._addopts

    @property
    def nbqa_ignore_cells(self) -> Sequence[str]:
        """Don't use, deprecated."""
        return self._ignore_cells

    @property
    def nbqa_process_cells(self) -> Sequence[str]:
        """Additional cells which nbqa should process."""
        return self._process_cells

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

        config.set_config(
            CONFIG_SECTIONS.ADDOPTS, [*self._addopts, *other.nbqa_addopts]
        )
        config.set_config(CONFIG_SECTIONS.CONFIG, self._config or other.nbqa_config)
        config.set_config(
            CONFIG_SECTIONS.IGNORE_CELLS, self._ignore_cells or other.nbqa_ignore_cells
        )
        config.set_config(
            CONFIG_SECTIONS.PROCESS_CELLS,
            self._process_cells or other.nbqa_process_cells,
        )
        config.set_config(CONFIG_SECTIONS.MUTATE, self._mutate or other.nbqa_mutate)
        config.set_config(CONFIG_SECTIONS.DIFF, self._diff or other.nbqa_diff)
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
        config.set_config(CONFIG_SECTIONS.PROCESS_CELLS, cli_args.nbqa_process_cells)
        config.set_config(CONFIG_SECTIONS.MUTATE, cli_args.nbqa_mutate)
        config.set_config(CONFIG_SECTIONS.DIFF, cli_args.nbqa_diff)
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
            CONFIG_SECTIONS.PROCESS_CELLS, DEFAULT_CONFIG["process_cells"].get(command)
        )
        defaults.set_config(
            CONFIG_SECTIONS.MUTATE, DEFAULT_CONFIG["mutate"].get(command)
        )
        defaults.set_config(CONFIG_SECTIONS.DIFF, DEFAULT_CONFIG["diff"].get(command))
        defaults.set_config(CONFIG_SECTIONS.FILES, DEFAULT_CONFIG["files"].get(command))
        defaults.set_config(
            CONFIG_SECTIONS.EXCLUDE, DEFAULT_CONFIG["exclude"].get(command)
        )

        return defaults

    def validate(self) -> None:
        """
        Check specified configs are valid.

        Raises
        ------
        ValueError
            If both --nbqa-diff and --nbqa-mutate are used together.
        FileNotFoundError
            If config file provided does not exist.
        """
        if self._diff and self._mutate:
            raise ValueError(
                dedent(
                    """\
                    Cannot use both `--nbqa-diff` and `--nbqa-mutate` flags together!

                    Use `--nbqa-diff` to preview changes, and `--nbqa-mutate` to apply them.
                    """
                )
            )
        if self.nbqa_config and not Path(self.nbqa_config).exists():
            raise FileNotFoundError(f"{self.nbqa_config} not found.")
        if self.nbqa_ignore_cells:
            raise ValueError(
                "--nbqa-ignore-cells is deprecated since version 0.6.0, "
                "most cell magics are now excluded by default."
            )
