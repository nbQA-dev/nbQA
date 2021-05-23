=================
Known limitations
=================

``nbQA`` is shy about processing magics. If a cell starts with a cell magic, then the rest of the cell
will be processed. What won't be processed will be:

- cells with cell magic where the cell magic isn't in the first line;
- cells with assignments to magic, e.g. ``flake8_version = !flake8 --version``;
- cells with multiple magics per line.
