====
nbQA
====

.. image:: https://dev.azure.com/megorelli/megorelli/_apis/build/status/MarcoGorelli.nbQA?branchName=master
          :target: https://dev.azure.com/megorelli/megorelli/_build/latest?definitionId=1&branchName=master

.. image:: https://img.shields.io/azure-devops/coverage/megorelli/megorelli/1/master.svg
          :target: https://dev.azure.com/megorelli/megorelli/_build/latest?definitionId=1&branchName=master

Adapter to run any code-quality tool on a Jupyter notebook.

E.g. just as you would run `flake8` against a Python file

.. code-block:: bash

    flake8 my_python_file.py

you can now just as easily run it against a Jupyter notebook by prepending `nbqa`:

.. code-block:: bash

    nbqa flake8 my_notebook.ipynb

Installation: nbQA has no dependencies, so as long as you have Python3.6+, you can do

.. code-block:: bash

    pip install -U nbqa

and it'll work without conflicting with any of your existing installs!
