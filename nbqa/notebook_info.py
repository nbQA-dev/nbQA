"""Store information about the code cells for processing."""

from typing import Mapping, NamedTuple, Sequence, Set

from nbqa.handle_magics import MagicHandler


class NotebookInfo(NamedTuple):
    """
    Store information about notebook cells used for processing.

    Attributes
    ----------
    cell_mapping
        Mapping from Python line numbers to Jupyter notebooks cells.
    trailing_semicolons
        Cell numbers where there were originally trailing semicolons.
    temporary_lines
        Mapping from cell number to all the magics substituted in those cell.
    code_cells_to_ignore
        List of code cell to ignore when modifying the source notebook.
    """

    cell_mappings: Mapping[int, str]
    trailing_semicolons: Set[int]
    temporary_lines: Mapping[int, Sequence[MagicHandler]]
    code_cells_to_ignore: Set[int]
