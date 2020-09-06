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

Adapter to run any standard code-quality tool on a Jupyter notebook. Documentation is hosted here_.

Installation
------------

Install :code:`nbqa` with `pip`_:

.. code-block:: bash

    pip install -U nbqa

Examples
--------

Reformat your notebook with `black`_:

.. code-block:: bash

    $ nbqa black my_notebook.ipynb --line-length=96 --nbqa-mutate
    reformatted my_notebook.ipynb
    All done! ✨ 🍰 ✨
    1 files reformatted.

Sort your imports with `isort`_:

.. code-block:: bash

    $ nbqa isort my_notebook.ipynb --treat-comment-as-code='# %%' --nbqa-mutate
    Fixing my_notebook.ipynb

Check your type annotations with `mypy`_:

.. code-block:: bash

    $ nbqa mypy my_notebook.ipynb --ignore-missing-imports
    my_notebook.ipynb:cell_10:5: error: Argument "num1" to "add" has incompatible type "str"; expected "int"

Run your docstring tests with `doctest`_:

.. code-block:: bash

    $ nbqa doctest my_notebook.ipynb
    **********************************************************************
    File "my_notebook.ipynb", cell_2:11, in my_notebook.add
    Failed example:
        add(2, 2)
    Expected:
        4
    Got:
        5
    **********************************************************************
    1 items had failures:
    1 of   2 in my_notebook.hello
    ***Test Failed*** 1 failures.

Configuration
-------------

Here's an example :code:`nbqa.ini` file - see `configuration`_ for more on configuration:

.. code-block:: ini

    [isort]
    config = setup.cfg
    mutate = 1
    addopts = --treat-comment-as-code '# %%%%'

    [flake8]
    config = setup.cfg

Usage as pre-commit hook
------------------------

If you want to use :code:`nbqa` with `pre-commit`_, here's an example of what you
could add to your :code:`.pre-commit-config.yaml` file:

.. code-block:: yaml

  - repo: https://github.com/nbQA-dev/nbQA
    rev: 0.1.28
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

Supported third party packages
------------------------------

In theory, :code:`nbqa` can adapt any Python code-quality tool to a Jupyter Notebook.

In practice, here are the tools it's been tested with:

- flake8_
- black_
- isort_
- mypy_
- doctest_

Contributing
------------

I will give write-access to anyone who contributes anything useful (e.g. pull request / bug report) - see the `contributing guide`_ for details on how to do so.

.. _flake8: https://flake8.pycqa.org/en/latest/
.. _black: https://black.readthedocs.io/en/stable/
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
.. _nb_black: https://github.com/dnanhkhoa/nb_black
.. _contributing guide: https://nbqa.readthedocs.io/en/latest/contributing.html
.. _configuration: https://nbqa.readthedocs.io/en/latest/configuration.html
