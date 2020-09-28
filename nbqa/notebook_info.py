"""Store information about the code cells for processing."""
from typing import Dict, Mapping, Set


class NotebookInfo:
    """
    Store information about notebook cells used for processing.

    Attributes
    ----------
    cell_mapping
        Mapping from Python line numbers to Jupyter notebooks cells.
    trailing_semicolons
        Cell numbers where there were originally trailing semicolons.
    temporary_lines
        Mapping from temporary lines to original lines.
    code_cells_to_ignore
        List of code cell to ignore when modifying the source notebook.
    """

    _cell_mappings: Dict[int, str] = {}
    _trailing_semicolons: Set[int] = set()
    _temporary_lines: Dict[str, str] = {}
    _code_cells_to_ignore: Set[int] = set()

    def __init__(
        self,
        cell_mappings: Dict[int, str],
        trailing_semicolons: Set[int],
        temporary_lines: Dict[str, str],
        code_cells_to_ignore: Set[int],
    ) -> None:
        """
        Initialize current NotebookInfo instance.

        Parameters
        ----------
        cell_mappings : Dict[int, str]
            Mapping from Python line numbers to Jupyter notebooks cells.
        trailing_semicolons : Set[int]
            Cell numbers where there were originally trailing semicolons.
        temporary_lines : Dict[str, str]
            Mapping from temporary lines to original lines.
        code_cells_to_ignore : Set[int]
            List of cell numbers to ignore when modifying the source notebook.
        """
        self._cell_mappings = cell_mappings
        self._trailing_semicolons = trailing_semicolons
        self._temporary_lines = temporary_lines
        self._code_cells_to_ignore = code_cells_to_ignore

    @property
    def cell_mappings(self) -> Mapping[int, str]:
        """Return mapping from Python line numbers to Jupyter notebooks cells."""
        return self._cell_mappings

    @property
    def trailing_semicolons(self) -> Set[int]:
        """Return cell numbers where there were originally trailing semicolons."""
        return self._trailing_semicolons

    @property
    def temporary_lines(self) -> Mapping[str, str]:
        """Return mapping from temporary lines to original lines."""
        return self._temporary_lines

    @property
    def code_cells_to_ignore(self) -> Set[int]:
        """Return code cell numbers to ignore when modifying the source notebook."""
        return self._code_cells_to_ignore
