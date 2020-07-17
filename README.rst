====
nbQA
====

.. image:: https://dev.azure.com/megorelli/megorelli/_apis/build/status/MarcoGorelli.nbQA?branchName=master
          :target: https://dev.azure.com/megorelli/megorelli/_build/latest?definitionId=1&branchName=master

.. image:: https://img.shields.io/azure-devops/coverage/megorelli/megorelli/1/master.svg
          :target: https://dev.azure.com/megorelli/megorelli/_build/latest?definitionId=1&branchName=master

Adapter to run any code-quality tool on a Jupyter notebook.

The general command is

.. code-block:: bash

    nbqa <command> <root directory> <flags for command>

For example, you could run:

.. code-block:: bash

    nbqa flake8 my_notebook.ipynb
    nbqa black . --check
    nbqa mypy --missing-imports
    nbqa pytest . --doctest-modules

Installation: nbQA has no dependencies, so as long as you have Python3.6+, you can do

.. code-block:: bash

    pip install -U nbqa

and it'll work without conflicting with any of your existing installs!

Supported third party packages
------------------------------

In theory, `nbqa` can adapt any Python code-quality tool to a Jupyter Notebook.

In practice, here are the tools I've actually tested:
- flake8
- black
- pytest
- mypy (make sure you will need to have `__init__` files in each subdirectory)
- doctest (as long as you run it via `pytest` with the `--doctest-modules` flag)
