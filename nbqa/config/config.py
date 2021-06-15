"""Module responsible for storing and handling nbqa configuration."""

from textwrap import dedent
from typing import TYPE_CHECKING, Callable, Optional, Sequence, Union

from nbqa.cmdline import CLIArgs

ConfigParser = Callable[[str], Union[str, bool, Sequence[str]]]

if TYPE_CHECKING:
    from typing import TypedDict
else:
    TypedDict = dict


class Configs(TypedDict):
    """nbQA-specific configs."""

    addopts: Sequence[str]
    diff: bool
    exclude: Optional[str]
    files: Optional[str]
    mutate: bool
    process_cells: Sequence[str]
    skip_bad_cells: bool


def merge(this: Configs, other: Configs) -> Configs:
    """
    Merge another Config instance with this instance.

    Returns
    -------
    Configs
        Merged configuration object
    """
    addopts = [*this["addopts"], *other["addopts"]]
    process_cells = this["process_cells"] or other["process_cells"]
    mutate = this["mutate"] or other["mutate"]
    diff = this["diff"] or other["diff"]
    files = this["files"] or other["files"]
    exclude = this["exclude"] or other["exclude"]
    skip_bad_cells = this["skip_bad_cells"] or other["skip_bad_cells"]
    return Configs(
        addopts=addopts,
        diff=diff,
        exclude=exclude,
        files=files,
        mutate=mutate,
        process_cells=process_cells,
        skip_bad_cells=skip_bad_cells,
    )


def parse_from_cli_args(cli_args: CLIArgs) -> Configs:
    """
    Parse nbqa configuration from command line arguments.

    Returns
    -------
    Configs
        Configuration passed via command line arguments.
    """
    return Configs(
        addopts=cli_args.nbqa_addopts,
        diff=cli_args.nbqa_diff,
        exclude=cli_args.nbqa_exclude,
        files=cli_args.nbqa_files,
        mutate=cli_args.nbqa_mutate,
        process_cells=cli_args.nbqa_process_cells,
        skip_bad_cells=cli_args.nbqa_skip_bad_cells,
    )


def get_default_config() -> Configs:
    """Get defaults."""
    return Configs(
        addopts=[],
        diff=False,
        exclude=None,
        files=None,
        mutate=False,
        process_cells=[],
        skip_bad_cells=False,
    )


def validate(configs: Configs) -> None:
    """
    Check specified configs are valid.

    Raises
    ------
    ValueError
        If both --nbqa-diff and --nbqa-mutate are used together.
    """
    if configs["diff"] and configs["mutate"]:
        raise ValueError(
            dedent(
                """\
                Cannot use both `--nbqa-diff` and `--nbqa-mutate` flags together!

                Use `--nbqa-diff` to preview changes, and `--nbqa-mutate` to apply them.
                """
            )
        )
