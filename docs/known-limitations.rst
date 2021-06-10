=================
Known limitations
=================

``nbQA`` is shy about processing magics. If a cell starts with a cell magic, then the rest of the cell
will be processed. What won't be processed will be:

- cells with multi-line magics;
- automagics (these will likely throw syntax errors. You can get around this by using the ``--skip-bad-cells`` flag, see :ref:`configuration<configuration>`).

Any other limitation is likely unintentional - if you run into any, please do report an issue.
