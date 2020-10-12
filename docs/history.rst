=========
Changelog
=========

0.3.0 (2020-10-12)
------------------

Added support for `pylint` (thanks Girish Pasupathy!).
Fixed a false-positive in `black` when cells ended with trailing semicolons.
Fixed some false-positives in `flake8` regarding expected numbers of newlines.

0.2.3 (2020-10-06)
------------------

Output from third-party tools is more consistent with the path the user passes in. E.g.
if the user passes a relative path, the output will show a relative path, whilst if the
user passes an absolute path, the output will show an absolute path.
Users are also now encouraged to report bugs if there are errors parsing / reconstructing
notebooks.

0.2.2 (2020-10-01)
------------------

Optimised handling cell-magics and improved support for indented in-line magics (thanks Girish Pasupathy!).

0.2.1 (2020-09-27)
------------------

Fix bug in which cells with trailing semicolons followed by empty newlines were having semicolons added to the newline.
Added support for ``pyupgrade``.

0.2.0 (2020-09-26)
------------------

First somewhat stable release, with ``flake8``, ``black``, ``isort``, ``mypy``, and ``doctest`` supported, and configuration via ``pyproject.toml``.
