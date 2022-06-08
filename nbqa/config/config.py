"""Module responsible for storing and handling nbqa configuration."""

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
    process_cells: Sequence[str]
    dont_skip_bad_cells: bool
    skip_celltags: Sequence[str]
    md: bool
    shell: bool


def get_default_config() -> Configs:
    """Get defaults."""
    return Configs(
        addopts=[],
        diff=False,
        exclude=None,
        files=None,
        process_cells=[],
        dont_skip_bad_cells=False,
        skip_celltags=[],
        md=False,
        shell=False,
    )
