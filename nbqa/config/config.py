"""Module responsible for storing and handling nbqa configuration."""

import collections
from shlex import split
from textwrap import dedent
from typing import Any, Callable, ClassVar, Dict, Optional, Sequence, Union

from nbqa.cmdline import CLIArgs
from nbqa.config.default_config import DEFAULT_CONFIG

ConfigParser = Callable[[str], Union[str, bool, Sequence[str]]]


class _ConfigSections(
    collections.namedtuple(
        "_ConfigSections",
        (
            "ADDOPTS",
            "PROCESS_CELLS",
            "MUTATE",
            "DIFF",
            "FILES",
            "EXCLUDE",
            "SKIP_BAD_CELLS",
        ),
    )
):
    """Config sections."""

    __slots__ = ()

    def __new__(  # pylint: disable=R0913
        cls,
        ADDOPTS: str = "addopts",
        PROCESS_CELLS: str = "process_cells",
        MUTATE: str = "mutate",
        DIFF: str = "diff",
        FILES: str = "files",
        EXCLUDE: str = "exclude",
        SKIP_BAD_CELLS: str = "skip_bad_cells",
    ) -> "_ConfigSections":
        """Python3.6.0 doesn't support defaults for namedtuples."""
        return super().__new__(
            cls, ADDOPTS, PROCESS_CELLS, MUTATE, DIFF, FILES, EXCLUDE, SKIP_BAD_CELLS
        )


CONFIG_SECTIONS = _ConfigSections()


class Configs:
    """Nbqa configuration."""

    CONFIG_SECTION_PARSERS: ClassVar[Dict[str, ConfigParser]] = {}
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.ADDOPTS] = (
        lambda arg: split(arg) if isinstance(arg, str) else arg
    )
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.PROCESS_CELLS] = (
        lambda arg: arg.split(",") if isinstance(arg, str) else arg
    )
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.MUTATE] = bool
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.DIFF] = bool
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.FILES] = str
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.EXCLUDE] = str
    CONFIG_SECTION_PARSERS[CONFIG_SECTIONS.SKIP_BAD_CELLS] = bool

    _mutate: bool = False
    _process_cells: Sequence[str] = []
    _addopts: Sequence[str] = []
    _diff: bool = False
    _files: Optional[str] = None
    _exclude: Optional[str] = None
    _skip_bad_cells: bool = False

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
    def nbqa_addopts(self) -> Sequence[str]:
        """Additional options to be passed to the third party command to run."""
        return self._addopts

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

    @property
    def nbqa_skip_cells(self) -> bool:
        """Skip cells with syntax errors."""
        return self._skip_bad_cells

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
        config.set_config(
            CONFIG_SECTIONS.PROCESS_CELLS,
            self._process_cells or other.nbqa_process_cells,
        )
        config.set_config(CONFIG_SECTIONS.MUTATE, self._mutate or other.nbqa_mutate)
        config.set_config(CONFIG_SECTIONS.DIFF, self._diff or other.nbqa_diff)
        config.set_config(CONFIG_SECTIONS.FILES, self._files or other.nbqa_files)
        config.set_config(CONFIG_SECTIONS.EXCLUDE, self._exclude or other.nbqa_exclude)
        config.set_config(
            CONFIG_SECTIONS.SKIP_BAD_CELLS,
            self._skip_bad_cells or other.nbqa_skip_cells,
        )
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
        config.set_config(CONFIG_SECTIONS.PROCESS_CELLS, cli_args.nbqa_process_cells)
        config.set_config(CONFIG_SECTIONS.MUTATE, cli_args.nbqa_mutate)
        config.set_config(CONFIG_SECTIONS.DIFF, cli_args.nbqa_diff)
        config.set_config(CONFIG_SECTIONS.FILES, cli_args.nbqa_files)
        config.set_config(CONFIG_SECTIONS.EXCLUDE, cli_args.nbqa_exclude)
        config.set_config(CONFIG_SECTIONS.SKIP_BAD_CELLS, cli_args.nbqa_skip_bad_cells)

        return config

    @staticmethod
    def get_default_config(command: str) -> "Configs":
        """Merge defaults."""
        defaults: Configs = Configs()
        defaults.set_config(
            CONFIG_SECTIONS.ADDOPTS, DEFAULT_CONFIG["addopts"].get(command)
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
        defaults.set_config(
            CONFIG_SECTIONS.SKIP_BAD_CELLS,
            DEFAULT_CONFIG["skip_bad_cells"].get(command),
        )

        return defaults

    def validate(self) -> None:
        """
        Check specified configs are valid.

        Raises
        ------
        ValueError
            If both --nbqa-diff and --nbqa-mutate are used together.
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
