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

.. raw:: html

    <p align="center">
        <a href="#readme">
            <img alt="demo" src="https://raw.githubusercontent.com/nbQA-dev/nbQA-demo/master/demo.gif">
        </a>
    </p>

Adapter to run any code-quality tool on a Jupyter notebook.
This is intended to be run as a `pre-commit`_ hook and/or during continuous integration.

Documentation is hosted here_.

Installation
------------

Install :code:`nbqa` with `pip`_:

.. code-block:: bash

    $ pip install nbqa

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

Configuration
-------------

You can configure :code:`nbQA` either at the command line, or by using a :code:`.nbqa.ini` file. We'll see some examples below.

Extra flags
~~~~~~~~~~~

If you wish to pass extra flags (e.g. :code:`--ignore W503` to :code:`flake8`) you can either run

.. code-block:: bash

    nbqa flake8 my_notebook.ipynb --ignore W503

or you can put the following in your :code:`.nbqa.ini` file

.. code-block:: ini

    [flake8]
    addopts = --ignore W503

Config file
~~~~~~~~~~~

If you already have a config file for your third-party tool (e.g. :code:`.mypy.ini` for :code:`mypy`), you can run

.. code-block:: bash

    nbqa mypy my_notebook.ipynb --nbqa-config .mypy.ini

or you can put the following in your :code:`.nbqa.ini` file

.. code-block:: ini

    [mypy]
    config = .mypy.ini

Allow mutations
~~~~~~~~~~~~~~~

By default, :code:`nbQA` won't modify your notebooks. If you wish to let your third-party tool modify your notebooks, you can
either pass the :code:`--nbqa-mutate` flag at the command-line, e.g.

.. code-block:: bash

    nbqa black my_notebook.ipynb --nbqa-mutate

or you can put the following in your :code:`.nbqa.ini` file

.. code-block:: ini

    [black]
    mutate = 1

Usage as pre-commit hook
------------------------

If you want to use :code:`nbqa` with `pre-commit`_, here's an example of what you
could add to your :code:`.pre-commit-config.yaml` file:

.. code-block:: yaml

  - repo: https://github.com/nbQA-dev/nbQA
    rev: 0.1.21
    hooks:
      - id: nbqa
        args: ['flake8']
        name: nbqa-flake8
        alias: nbqa-flake8
        additional_dependencies: ['flake8']
      - id: nbqa
        args: ['isort', '--nbqa-mutate']
        name: nbqa-isort
        alias: nbqa-isort
        additional_dependencies: ['isort']
      - id: nbqa
        args: ['mypy']
        name: nbqa-mypy
        alias: nbqa-mypy
        additional_dependencies: ['mypy']

Supported third party packages
------------------------------

In theory, :code:`nbqa` can adapt any Python code-quality tool to a Jupyter Notebook.

In practice, here are the tools it's been tested with:

- flake8_
- black_
- pytest_
- isort_
- mypy_
- doctest_ (as long as you run it via pytest_ with the `--doctest-modules` flag)

See Also
--------

Here are some other code quality tools for Jupyter Notebooks:

- `flake8-nb`_ (apply `flake8`_ to notebook);
- `black-nb`_ (apply `black`_ to notebook);
- `nbstripout`_ (clear notebook cells' outputs);
- `jupyterlab_code_formatter`_ (Jupyter Lab plugin);

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
.. _`nbstripout`: https://github.com/kynan/nbstripout
.. _`jupyterlab_code_formatter`: https://github.com/ryantam626/jupyterlab_code_formatter
.. _pip: https://pip.pypa.io
