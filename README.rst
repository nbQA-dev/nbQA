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

Adapter to run any code-quality tool on a Jupyter notebook. Zero dependencies, runs on Python3.6+.
Documentation is hosted here_.

Installation
------------

Install :code:`nbqa` with

.. code-block:: bash

    pip install nbqa

Quickstart
----------

The general syntax is

.. code-block:: bash

    nbqa <command> <directory or file> <flags>

Example of commands you can do:

.. code-block:: bash

    nbqa flake8 my_notebook.ipynb
    nbqa black . --check
    nbqa mypy --missing-imports
    nbqa pytest . --doctest-modules

Note that you will need to have your desired third-party tool installed - e.g., to run the first example above, you will need to have flake8_ installed.

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

Here are some other code quality tools for Jupyter Notebooks:

- flake-nb_;
- black-nb_.

Project template from cookiecutter_.

.. _cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _black: https://black.readthedocs.io/en/stable/
.. _pytest: https://docs.pytest.org/en/latest/
.. _isort: https://timothycrosley.github.io/isort/
.. _mypy: http://mypy-lang.org/
.. _doctest: https://docs.python.org/3/library/doctest.html
.. _black: https://github.com/tomcatling/black-nb
.. _flake8-nb: https://flake8-nb.readthedocs.io/en/latest/readme.html
.. _here: https://nbqa.readthedocs.io/en/latest/
