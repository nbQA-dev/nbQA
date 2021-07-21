=================
Known limitations
=================

By default, ``nbQA`` will skip cells with invalid syntax.
If you choose to process cells with invalid syntax via the ``--nbqa-dont-skip-bad-cells`` flag (see :ref:`configuration<configuration>`),
then the following will still not be processed:

- cells with multi-line magics;
- automagics (ideas for how to detect them statically are welcome!);
- cells with code which ``IPython`` would transform magics into (e.g. ``get_ipython().system('ls')``).

Any other limitation is likely unintentional - if you run into any, please do report an issue.
