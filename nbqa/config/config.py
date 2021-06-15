"""Module responsible for storing and handling nbqa configuration."""

from textwrap import dedent
from typing import TYPE_CHECKING, Callable, Optional, Sequence, Union

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
    dont_skip_bad_cells: bool
    skip_celltags: Sequence[str]


def get_default_config() -> Configs:
    """Get defaults."""
    return Configs(
        addopts=[],
        diff=False,
        exclude=None,
        files=None,
        mutate=False,
        process_cells=[],
        dont_skip_bad_cells=False,
        skip_celltags=[],
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
