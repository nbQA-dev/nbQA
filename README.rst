.. image:: https://github.com/nbQA-dev/nbQA/raw/master/assets/logo.png
  :width: 400

====
nbQA
====

.. image:: https://github.com/nbQA-dev/nbQA/workflows/tox/badge.svg
          :target: https://github.com/nbQA-dev/nbQA/actions?workflow=tox

.. image:: https://codecov.io/gh/nbQA-dev/nbQA/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/nbQA-dev/nbQA

.. image:: https://badge.fury.io/py/nbqa.svg
    :target: https://badge.fury.io/py/nbqa

.. image:: https://readthedocs.org/projects/nbqa/badge/?version=latest&style=plastic
    :target: https://nbqa.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/pyversions/nbqa.svg
    :target: https://pypi.org/project/nbqa/

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: http://mypy-lang.org/

.. image:: https://interrogate.readthedocs.io/en/latest/_static/interrogate_badge.svg
   :target: https://github.com/econchick/interrogate

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pylint-10/10-brightgreen.svg
   :target: https://github.com/PyCQA/pylint

Adapter to run any code-quality tool on a Jupyter notebook.
This is intended to be run as a `pre-commit`_ hook and/or during continuous integration.

Documentation is hosted here_.

Prerequisites
-------------
If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Installation
------------

Install :code:`nbqa` with

.. code-block:: bash

    $ pip install nbqa

There are **no dependencies** for :code:`nbqa` so installation should be lightning-fast.
Check your installation with

.. code-block:: bash

    $ nbqa --version
    nbqa 0.1.16

Quickstart
----------

The general syntax is

.. code-block:: bash

    nbqa <command> <notebook or directory> <args>

where :code:`command` is any standard Python code quality tool.

Examples
--------

Check static type annotations:

.. code-block:: bash

    $ nbqa mypy tweet-sentiment-roberta-pytorch.ipynb --ignore-missing-imports
    tweet-sentiment-roberta-pytorch.ipynb:cell_10:5: error: Argument "batch_size" to "get_test_loader" has incompatible type "str"; expected "int"

Check any examples in your docstrings are correct:

.. code-block:: bash

    $ nbqa pytest tweet-sentiment-roberta-pytorch.ipynb --doctest-modules
    ============================= test session starts ==============================
    platform linux -- Python 3.8.2, pytest-5.4.3, py-1.9.0, pluggy-0.13.1
    rootdir: /home/marco/tweet-sentiment-extraction
    plugins: cov-2.10.0
    collected 3 items

    tweet-sentiment-roberta-pytorch.ipynb .                                  [100%]

    ============================== 1 passed in 0.03s ===============================

Format your notebooks using :code:`black`:

.. code-block:: bash

    $ nbqa black . --line-length=96 --nbqa-mutate
    reformatted tweet-sentiment-roberta-pytorch.ipynb
    All done! ✨ 🍰 ✨
    1 files reformatted.

Note that if, as in this last example, you expect your notebooks to be modified, you will need to
pass the :code:`--nbqa-mutate` flag (alternatively, you could set :code:`mutate=1` in your :code:`.nbqa.ini`
file, see "Configuration").

Empty :code:`__init__.py` files
-------------------------------

Some tools, such as :code:`mypy`, require (possibly empty) :code:`__init__.py` files to be in each subdirectory you wish to analyse. To make :code:`nbQA` aware of this,
you need to pass the :code:`--nbqa-preserve-init` flag, e.g.

.. code-block:: bash

    nbqa mypy my_dir/my_subdir/my_notebook.ipynb --nbqa-preserve-init

Alternatively, you could set :code:`preserve_init=1` in your :code:`.nbqa.ini` file (see "Configuration").

Configuration
-------------

You can tell `nbQA` which config file to use either by using the :code:`--nbqa-config` flag, or by
specifying it in a :code:`.nbqa.ini` file.

So for example, if you wanted to run :code:`mypy` in such a way that it respects your :code:`.mypy.ini`
file _and_ with the :code:`--pretty` flag, then you could either run

.. code-block:: bash

    nbqa mypy my_notebook.ipynb --pretty --nbqa-config .mypy.ini --nbqa-preserve-init

or, you could put the following in your :code:`.nbqa.ini` file

.. code-block:: ini

    [mypy]
    addopts = --pretty
    config = .mypy.ini
    preserve_init = 1

and then simply run

.. code-block:: bash

    nbqa mypy my_notebook.ipynb

You can also tell :code:`nbQA` to allow mutations, e.g.

.. code-block:: ini

    [black]
    mutate=1

Usage as pre-commit hook
------------------------

If you want to use :code:`nbqa` with `pre-commit`_, here's an example of what you
could add to your :code:`.pre-commit-config.yaml` file:

.. code-block:: yaml

  - repo: https://github.com/nbQA-dev/nbQA
    rev: 0.1.16
    hooks:
      - id: nbqa
        args: ['flake8']
        name: nbqa-flake8
        additional_dependencies: ['flake8']
      - id: nbqa
        args: ['isort', '--nbqa-mutate']
        name: nbqa-isort
        additional_dependencies: ['isort']
      - id: nbqa
        args: ['mypy']
        name: nbqa-mypy
        additional_dependencies: ['mypy']

Supported third party packages
------------------------------

In theory, :code:`nbqa` can adapt any Python code-quality tool to a Jupyter Notebook.

In practice, here are the tools it's been tested with:

- flake8_
- black_
- pytest_
- isort_
- mypy_ (you will need to have `__init__` files in each subdirectory)
- doctest_ (as long as you run it via pytest_ with the `--doctest-modules` flag)

See Also
--------

Here are some specialised code quality tools for Jupyter Notebooks:

- `flake8-nb`_;
- `black-nb`_.

Project template from cookiecutter_.

.. _cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _black: https://black.readthedocs.io/en/stable/
.. _pytest: https://docs.pytest.org/en/latest/
.. _isort: https://timothycrosley.github.io/isort/
.. _mypy: http://mypy-lang.org/
.. _doctest: https://docs.python.org/3/library/doctest.html
.. _black-nb: https://github.com/tomcatling/black-nb
.. _flake8-nb: https://flake8-nb.readthedocs.io/en/latest/readme.html
.. _here: https://nbqa.readthedocs.io/en/latest/
.. _`pre-commit`: https://pre-commit.com/
