"""
Find project root.

Taken from https://github.com/psf/black/blob/master/src/black/__init__.py
"""

from functools import lru_cache
from pathlib import Path
from typing import Iterable

# files and folders known to indicate a project root
KNOWN_PROJECT_ROOT_DIRS = [".git", ".hg"]
KNOW_PROJECT_ROOT_FILES = [
    ".nbqa.ini",
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "MANIFEST.in",
]


@lru_cache()
def find_project_root(
    srcs: Iterable[str],
    root_files: Iterable[str] = tuple(KNOW_PROJECT_ROOT_FILES),
    root_dirs: Iterable[str] = tuple(KNOWN_PROJECT_ROOT_DIRS),
) -> Path:
    """
    Return a directory containing .git, .hg, or nbqa.ini.

    That directory will be a common parent of all files and directories
    passed in `srcs`.
    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.

    Parameters
    ----------
    srcs
        Source paths.
    root_files
        Files indicating that the current directory is the project root.

    Returns
    -------
    Path
        Project root.
    """
    path_srcs = [Path(Path.cwd(), src).resolve() for src in srcs]

    # A list of lists of parents for each 'src'. 'src' is included as a
    # "parent" of itself if it is a directory
    src_parents = [
        list(path.parents) + ([path] if path.is_dir() else []) for path in path_srcs
    ]

    common_base = max(
        set.intersection(*(set(parents) for parents in src_parents)),
        key=lambda path: path.parts,
    )

    for directory in (common_base, *common_base.parents):

        for known_project_root_dir in root_dirs:
            if (directory / known_project_root_dir).is_dir():
                return directory
        for know_project_root_file in root_files:
            if (directory / know_project_root_file).is_file():
                return directory

    return Path("/").resolve()
