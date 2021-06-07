=================
Known limitations
=================

``nbQA`` is shy about processing magics. If a cell starts with a cell magic, then the rest of the cell
will be processed. What won't be processed will be:

- cells with cell magic where the cell magic isn't in the first line;
- cells with multi-line magics.

Automagics will also not be processed, and will likely throw syntax errors. You can get around this by using
the ``--skip-bad-cells`` flag (see :ref:`configuration<configuration>`).
