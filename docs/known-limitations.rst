=================
Known limitations
=================

By default, ``nbQA`` will skip cells with invalid syntax.
If you choose to process cells with invalid syntax via the ``--nbqa-dont-skip-bad-cells`` flag (see :ref:`configuration<configuration>`),
then the following will still not be processed:

- cells with multi-line magics;
- automagics (ideas for how to detect them statically are welcome!);
- cells with code which ``IPython`` would transform magics into (e.g. ``get_ipython().system('ls')``).

Because ``nbQA`` converts the code cells in Jupyter notebooks to temporary Python files for linting, certain flags like ``flake8``'s
``--per-file-ignores`` don't work perfectly.
The temporary Python files will not match the specified file patterns and ignored error codes will still
surface (`GH issue <https://github.com/nbQA-dev/nbQA/issues/730>`_).
nbqa-generated temporary files will contain the string ``nbqa_ipynb``,
so you can still apply per-file-ignores if you add an additional pattern:

.. sourcecode:: ini

    [flake8]
    per-file-ignores =
      examples/*.ipynb: E402
      examples/*nbqa_ipynb.py: E402

The directory and the stem of the filename are preserved, so e.g. ``path/to/mynotebook.ipynb`` will be ``path/to/mynotebook{randomstring}_nbqa_ipynb.py`` when nbqa passes it to the linter.

Any other limitation is likely unintentional - if you run into any, please do report an issue.
