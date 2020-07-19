.. image:: https://github.com/MarcoGorelli/nbQA/raw/master/assets/output-onlinepngtools.png
  :width: 400

====
nbQA
====

.. image:: https://dev.azure.com/megorelli/megorelli/_apis/build/status/MarcoGorelli.nbQA?branchName=master
          :target: https://dev.azure.com/megorelli/megorelli/_build/latest?definitionId=1&branchName=master

.. image:: https://img.shields.io/azure-devops/coverage/megorelli/megorelli/1/master.svg
          :target: https://dev.azure.com/megorelli/megorelli/_build/latest?definitionId=1&branchName=master

.. image:: https://badge.fury.io/py/nbqa.svg
    :target: https://badge.fury.io/py/nbqa

.. image:: https://readthedocs.org/projects/nbqa/badge/?version=latest&style=plastic
    :target: https://nbqa.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/pyversions/nbqa.svg
    :target: https://pypi.org/project/nbqa/

Adapter to run any code-quality tool on a Jupyter notebook. Documentation is hosted here_.

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

Check your installation with

.. code-block:: bash

    $ nbqa --version
    nbqa 0.1.3

Quickstart
----------

The general syntax is

.. code-block:: bash

    nbqa <command> <notebook or directory> <args>

, where :code:`command` is any Python code quality tool. For example, you could run:

.. code-block:: bash

    $ nbqa flake8 my_notebook.ipynb
    $ nbqa black my_notebook.ipynb --check
    $ nbqa mypy my_notebook.ipynb --ignore-missing-imports
    $ nbqa pytest my_notebook.ipynb --doctest-modules

You can also pass an entire directory instead of a single file, e.g. :code:`nbqa flake8 my_notebooks`.

Examples
--------

Format your notebooks using :code:`black`:

.. code-block:: bash

    $ nbqa black .
    reformatted tweet-sentiment-roberta-pytorch.ipynb
    All done! ✨ 🍰 ✨
    1 files reformatted.

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

Configuration
-------------

You can pass extra configurations to your tools either via the command line (as in the
examples above), or in a :code:`.nbqa.ini` file, which could look something like this:

.. code-block:: ini

    [black]
    line-length=96

    [flake8]
    max-line-length=88
    ignore=E203,W503,W504

Flags from this :code:`.ini` will be passed to :code:`nbqa` as they're written.

Usage as pre-commit hook
------------------------

If you want to use :code:`nbqa` with `pre-commit`_, here's an example of what you
could add to your :code:`.pre-commit-config.yaml` file:

.. code-block::yaml

  - repo: https://github.com/MarcoGorelli/nbQA-mirror-0
    rev: master
    hooks:
      - id: nbqa
        args: ['flake8']
  - repo: https://github.com/MarcoGorelli/nbQA-mirror-1
    rev: master
    hooks:
      - id: nbqa
        args: ['isort']

Note that, because the repository keys need to be unique, you will need to use a
different mirror repository for each pre-commit hook you wish to use.

See Also
--------

Here are some other code quality tools for Jupyter Notebooks:

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
