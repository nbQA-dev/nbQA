"""Module responsible for storing and handling nbqa configuration."""

from collections import defaultdict
from pathlib import Path
from shlex import split
from textwrap import dedent
from typing import (
    Any,
    Callable,
    ClassVar,
    DefaultDict,
    Dict,
    List,
    Mapping,
    NamedTuple,
    Optional,
)

import toml
from pkg_resources import resource_filename

from nbqa.cmdline import CLIArgs

CONFIG_FILES: DefaultDict[str, List[str]] = defaultdict(
    lambda: ["setup.cfg", "tox.ini", "pyproject.toml"]
)
CONFIG_FILES["black"] = ["pyproject.toml"]
CONFIG_FILES["check-ast"] = []
CONFIG_FILES["doctest"] = []
CONFIG_FILES["flake8"] = ["setup.cfg", "tox.ini", ".flake8"]
CONFIG_FILES["isort"] = [
    ".isort.cfg",
    "pyproject.toml",
    "setup.cfg",
    "tox.ini",
    ".editorconfig",
]
CONFIG_FILES["mypy"] = ["mypy.ini", ".mypy.ini", "setup.cfg"]
CONFIG_FILES["pylint"] = ["pylintrc", ".pylintrc", "pyproject.toml", "setup.cfg"]
CONFIG_FILES["pyupgrade"] = []


class _ConfigSections(NamedTuple):  # pylint: disable=R0903
    """Stores all the config section names."""

    ADDOPTS: str = "addopts"
    CONFIG: str = "config"
    IGNORE_CELLS: str = "ignore_cells"
    MUTATE: str = "mutate"
    DIFF: str = "diff"
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
        CONFIG_SECTIONS.DIFF: bool,
        CONFIG_SECTIONS.FILES: str,
        CONFIG_SECTIONS.EXCLUDE: str,
    }

    _mutate: bool = False
    _config: Optional[str] = None
    _ignore_cells: List[str] = []
    _addopts: List[str] = []
    _diff: bool = False
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
    def nbqa_diff(self) -> bool:
        """Show diff instead of replacing notebook code."""
        return self._diff

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
            CONFIG_SECTIONS.IGNORE_CELLS, DEFAULT_CONFIG["ignore_cells"].get(command)
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

    def validate(self, command: str) -> None:
        """
        Check specified configs are valid.

        Parameters
        ----------
        command
            Code quality tool being run.

        Raises
        ------
        ValueError
            If both --nbqa-diff and --nbqa-mutate are used together, or if
            config file is not supported by given code quailty tool.
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
        if (
            self.nbqa_config
            and (
                command
                in [
                    i
                    for i in CONFIG_FILES
                    if CONFIG_FILES[i] != CONFIG_FILES.default_factory()  # type: ignore
                ]
            )
            and self.nbqa_config not in CONFIG_FILES[command]
        ):
            # pylint: disable=C0301
            raise ValueError(
                dedent(
                    f"""\
                    {self.nbqa_config} is not a valid config file for '{command}'.

                    If you believe it is, please file an issue at https://github.com/nbQA-dev/nbQA/issues.
                    """
                )
            )
            # pylint: enable=C0301
