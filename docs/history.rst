=========
Changelog
=========

1.5.0 (???)
~~~~~~~~~~~
``nbqa`` now removes empty cells which were not empty to begin with.
Markdown files saved via ``Jupytext`` will now be processed as well
(thanks @basnijholt and @rgommers for the suggestion!)
If ``nbqa`` is passed an invalid notebook, it will exit 123. If it's
passed a non-Python notebook, it'll exit 0.

1.4.0 (2022-07-17)
~~~~~~~~~~~~~~~~~~
Added ``-nbqa-shell`` command (thanks @pwoolvett !).
Fixed entrypoint of ``pycodestyle`` hook (thanks @janosh !).

1.3.1 (2022-03-09)
~~~~~~~~~~~~~~~~~~
Fixed setup.cfg to mark than only Python3.7+ is supported.

1.3.0 (2022-03-05)
~~~~~~~~~~~~~~~~~~
Removed support for Python 3.6.
Exit code for ``--nbqa-diff`` is now ``1`` is file would've been modified, and ``0`` otherwise.
Cells with just line magics will now be ignored.

1.2.3 (2022-01-11)
~~~~~~~~~~~~~~~~~~
Removed (unnecessary) upper-bound on ``tomli``.

1.2.2 (2021-11-25)
~~~~~~~~~~~~~~~~~~
Fixed bug whereby constructs like ``var = %env var`` would not round-trip (thanks Daniel Sparing for the report!).
No longer add a trailing newline to notebooks which didn't have one originally.

1.2.1 (2021-11-21)
~~~~~~~~~~~~~~~~~~
Fixed bug whereby ``blacken-docs`` would need to be run as ``nbqa blacken_docs``,
because the package name and the Python module of ``blacken-docs`` differ.
Now, it can be run as ``nbqa blacken-docs``, as users would expect.

1.2.0 (2021-11-20)
~~~~~~~~~~~~~~~~~~
Added support for formatting markdown cells via the ``--nbqa-md`` flag.
Changed aesthetics of ``--nbqa-diff`` to be in line with how ``black`` does it.

1.1.1 (2021-09-12)
~~~~~~~~~~~~~~~~~~
Fixed bug whereby local module wasn't being picked up correctly.
Removed ``language_version`` from ``.pre-commit-hooks.yaml``.

1.1.0 (2021-08-01)
~~~~~~~~~~~~~~~~~~
Added support for ``autopep8`` and ``pydocstyle``.
Fixed bug whereby ``nbqa mypy`` wasn't showing coloured output.
Added several extra internal robustness checks.

1.0.0 (2021-07-21)
~~~~~~~~~~~~~~~~~~
Removed ``--nbqa-mutate`` flag, it's no longer necessary.
Options passed to ``--nbqa-addopts`` are now combined with those in ``pyproject.toml``, as opposed
to overriding them.

0.13.1 (2021-06-25)
~~~~~~~~~~~~~~~~~~~
Fixed bug whereby local scripts / modules could not be run by ``nbQA`` due to incorrect ``ModuleNotFoundError``.

0.13.0 (2021-06-15)
~~~~~~~~~~~~~~~~~~~
BREAKING CHANGE: by default, cells with invalid syntax will now be skipped. To retain the old
behaviour, use ``--nbqa-dont-skip-bad-cells`` (see documentation for details / examples).
Added ability to skip cells based on celltags.

0.12.0 (2021-06-10)
~~~~~~~~~~~~~~~~~~~
``nbQA`` will no longer halt execution if it encounters notebooks which it
can't parse or which fail to reconstruct - instead, such errors will be reported
all at once at the end. The exit code in such cases will be ``123`` (as in the ``black``
formatter).
Fixed bug whereby DataBricks notebooks (which are saved differently than Jupyter notebooks) with empty cells were not being reconstructed properly
when using ``nbqa-diff``.
Cell magics are now parsed more robustly.

0.11.1 (2021-06-07)
~~~~~~~~~~~~~~~~~~~
Fixed historic limitation whereby cells with assignment to line magics or
to system outputs were being ignored.
Removed ``autoflake`` hook (at least until I am confident that magics are
fully supported).

0.10.0 (2021-05-30)
~~~~~~~~~~~~~~~~~~~
Introduced ``--nbqa-skip-bad-cells`` flag.
Cells with multi-line magics are no longer processed.

0.9.0 (2021-05-23)
------------------
Fixed bug whereby percent format sign was being mistaken for a line
IPython magic. ``nbQA`` is now intentionally more timid about processing
magics, and cells with unusual magics will be ignored.

0.8.1 (2021-05-15)
------------------
If output from tool cannot be parsed from Python lines to notebook
code cells, then a ``KeyError`` is no longer thrown and the original output
is printed (thanks Tony Hirst for the bug report!).

0.8.0 (2021-05-02)
------------------

Output from linters will now typically display relative paths where possible,
else absolute ones.
Flags ``--nbqa-ignore`` and ``--nbqa-config`` have been removed.
Fixed regression (introduced in 0.7.1) whereby if a series of notebooks
was passed and one of them did not exist, then the temporary files associated
with the first ones would not get cleaned up.

0.7.1 (2021-04-28)
------------------

Fixed regression (introduced in 0.7.0) whereby ``nbqa-flake8`` wasn't
reporting error messages with cell numbers if absolute path of notebook
was used.

0.7.0 (2021-04-18)
------------------

Fixed historic known limitation of ``nbqa-black`` removing trailing semicolons
when they were followed by comments.
Fixed bug whereby local modules were not properly being picked up by ``nbqa-mypy``
(thanks Rafal Wojdyla for the excellent bug report!).
Added support for ``yapf`` (thanks Bradley Dice for the suggestion + PR!).
Added support for Python3.6.0 (previously was 3.6.1+).

0.6.1 (2021-04-16)
------------------

Fixed bug whereby notebooks with dots in their names
were not being processed correctly (thank you Ivan Cheung for the issue!)

0.6.0 (2021-04-04)
------------------

Processing cell-magics is now opt-in rather than opt-out.
Original output from tool is always printed with ``--nbqa-diff``.

0.5.9 (2021-02-22)
------------------

Nothing, just fixing up the previous tag, sorry for the inconvenience caused.
xref https://github.com/pre-commit-ci/issues/issues/45

0.5.8 (2021-02-20)
------------------

Fixed bug in which ``mypy`` wasn't finding local imports due to
``MYPYPATH`` not being carried over by ``nbqa``.

0.5.7 (2021-01-26)
------------------

Fixed bug whereby ``pyupgrade`` wasn't working with empty notebook due to
``nbQA`` adding newlines to the end of the file even if the file was empty.

0.5.6 (2020-12-29)
------------------

Fixed bug whereby ``flake8`` with the ``wemake-python-styleguide`` plugin
was throwing false-positives about magic number being present when they weren't.

0.5.5 (2020-12-10)
------------------

Improved error parsing when ``nbqa black`` finds code which can't be parsed
(e.g. assignment to a literal).
You can now once again install all supported code-quality tools with
``python -m pip install -U nbqa[toolchain]`` (thanks Sebastian Weigand!).

0.5.4 (2020-12-06)
------------------

Fixed bug whereby notebooks starting with comments were being uncommented
out when replacing notebooks (thanks Nathan Cooper for filing the issue!).

0.5.3 (2020-12-04)
------------------

Fixed bug whereby commented-out cell magics were preventing ``nbqa`` from
reconstructing notebooks properly (thanks John Sandall for filing the issue!).

0.5.2 (2020-11-30)
------------------

Fixed bug whereby ``nbqa`` was throwing ``UnicodeDecodeError`` on Windows
(thanks Simon Brugman for noticing the issue and for submitting a fix!).

0.5.1 (2020-11-25)
------------------

Fixed bugs whereby ``nbqa`` wasn't handling incomplete IPython magics, nor was
it handling assignments to help magics (thanks Girish Pasupathy for noticing
and fixing both of these!).

0.5.0 (2020-11-22)
------------------

Fixed bug whereby formatters weren't parsing assignments to shell magic.
Raise error if given config file doesn't exist.
Added ``-nbqa-diff`` flag, which allows users to preview changes before applying them.
Added ``nbqa-autoflake`` pre-commit hook.

0.4.1 (2020-11-11)
------------------

Fixed bug whereby parsing notebooks without any code cells was throwing ``IndexError``.
Fixed bug whereby piping output to a text file was introducing extra newlines on Windows.
Added ``nbqa-check-ast`` pre-commit hook.
Added ``--nbqa-files`` and ``--nbqa-exclude`` flags for file inclusion/exclusion.

0.4.0 (2020-11-05)
------------------

Added support for inline magics (thanks Girish Pasupathy for this huge effort!).
Raise ``FileNotFoundError`` if non-existent notebook/directory is passed.
Fixed bug whereby ``FileNotFoundError`` was being raised if directory without notebooks in it was passed.
Users are encouraged to report bugs if we can't parse output from code quality tool.
Output from ``black`` refers to cell number rather than python line number if command fails.
More informative message is raised if ``nbqa`` is called without a code quality tool and a notebook/directory.
Added some more cell magics to list of cell magics ignored by default.
No longer use emojis in our own error reporting.
``.git``, ``.venv``, and other common non-source-code directories are excluded from recursive search for notebooks.
More tool-specific config files are preserved by default.

0.3.6 (2020-10-30)
------------------

Improved error reporting if file is not found.
We now pass ``--treat-comment-as-code '# %%'`` by default when running ``isort``.
Fixed bug whereby tools referencing line 0 we resulting in a ``KeyError``.

0.3.5 (2020-10-25)
------------------

Optimised how nbqa passes files so that pre-commit hooks run faster.

0.3.4 (2020-10-23)
------------------

Fixed bug whereby nbqa was giving the wrong error message when running ``nbqa doctest`` and
the notebook contained a library which couldn't be imported.

0.3.3 (2020-10-21)
------------------

More precise error diagnostics if code-quality tool isn't found (thanks Girish Pasupathy!).
You can now install all supported code-quality tools with ``python -m pip install -U nbqa[toolchain]`` (thanks Sebastian Weigand!).
We handle a greater array of cell magics by default.
We removed ``nbqa-doctest`` pre-commit hook, as this one's best run from the command line (thanks Sebastian Weigand!).

0.3.2 (2020-10-17)
------------------

In-built pre-commit hooks for ``black``, ``flake8``, ``mypy``, ``isort``, ``pyupgrade``, ``doctest``, and ``pylint`` are
now available.

0.3.1 (2020-10-16)
------------------

Fixed bug whereby ``nbqa`` was using the system (or virtual environment) Python, rather than
the Python used to install ``nbqa``. This was causing issues when running ``nbqa`` outside of a
virtual environment.

0.3.0 (2020-10-12)
------------------

Added support for ``pylint`` (thanks Girish Pasupathy!).
Fixed a false-positive in ``black`` when cells ended with trailing semicolons.
Fixed some false-positives in ``flake8`` regarding expected numbers of newlines.

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
