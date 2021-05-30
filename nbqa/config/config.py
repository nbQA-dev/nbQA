"""Module responsible for storing and handling nbqa configuration."""

from shlex import split
from textwrap import dedent
from typing import Any, Callable, ClassVar, Dict, Optional, Sequence, Union

from nbqa.cmdline import CLIArgs
from nbqa.config.default_config import DEFAULT_CONFIG

ConfigParser = Callable[[str], Union[str, bool, Sequence[str]]]


class Configs:
    """Nbqa configuration."""

    CONFIG_SECTION_PARSERS: ClassVar[Dict[str, ConfigParser]] = {}
    CONFIG_SECTION_PARSERS["addopts"] = (
        lambda arg: split(arg) if isinstance(arg, str) else arg
    )
    CONFIG_SECTION_PARSERS["process_cells"] = (
        lambda arg: arg.split(",") if isinstance(arg, str) else arg
    )
    CONFIG_SECTION_PARSERS["mutate"] = bool
    CONFIG_SECTION_PARSERS["diff"] = bool
    CONFIG_SECTION_PARSERS["files"] = str
    CONFIG_SECTION_PARSERS["exclude"] = str
    CONFIG_SECTION_PARSERS["skip_bad_cells"] = bool

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

        config.set_config("addopts", [*self._addopts, *other.nbqa_addopts])
        config.set_config(
            "process_cells",
            self._process_cells or other.nbqa_process_cells,
        )
        config.set_config("mutate", self._mutate or other.nbqa_mutate)
        config.set_config("diff", self._diff or other.nbqa_diff)
        config.set_config("files", self._files or other.nbqa_files)
        config.set_config("exclude", self._exclude or other.nbqa_exclude)
        config.set_config(
            "skip_bad_cells",
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

        config.set_config("addopts", cli_args.nbqa_addopts)
        config.set_config("process_cells", cli_args.nbqa_process_cells)
        config.set_config("mutate", cli_args.nbqa_mutate)
        config.set_config("diff", cli_args.nbqa_diff)
        config.set_config("files", cli_args.nbqa_files)
        config.set_config("exclude", cli_args.nbqa_exclude)
        config.set_config("skip_bad_cells", cli_args.nbqa_skip_bad_cells)

        return config

    @staticmethod
    def get_default_config(command: str) -> "Configs":
        """Merge defaults."""
        defaults: Configs = Configs()
        defaults.set_config("addopts", DEFAULT_CONFIG["addopts"].get(command))
        defaults.set_config(
            "process_cells", DEFAULT_CONFIG["process_cells"].get(command)
        )
        defaults.set_config("mutate", DEFAULT_CONFIG["mutate"].get(command))
        defaults.set_config("diff", DEFAULT_CONFIG["diff"].get(command))
        defaults.set_config("files", DEFAULT_CONFIG["files"].get(command))
        defaults.set_config("exclude", DEFAULT_CONFIG["exclude"].get(command))
        defaults.set_config(
            "skip_bad_cells",
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
