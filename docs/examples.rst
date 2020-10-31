=====================
Command-line examples
=====================
Reformat your notebooks with `black`_:

.. code:: console

   $ nbqa black my_notebook.ipynb --nbqa-mutate
   reformatted my_notebook.ipynb
   All done! ✨ 🍰 ✨
   1 files reformatted.

Sort your imports with `isort`_:

.. code:: console

   $ nbqa isort my_notebook.ipynb --nbqa-mutate
   Fixing my_notebook.ipynb

Check your type annotations with `mypy`_:

.. code:: console

   $ nbqa mypy my_notebook.ipynb --ignore-missing-imports
   my_notebook.ipynb:cell_10:5: error: Argument "num1" to "add" has incompatible type "str"; expected "int"

Run your docstring tests with `doctest`_:

.. code:: console

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

Check for style guide enforcement with `flake8`_:

.. code:: console

   $ nbqa flake8 my_notebook.ipynb --extend-ignore=E203,E302,E305,E703
   my_notebook.ipynb:cell_3:1:1: F401 'import pandas as pd' imported but unused

Upgrade your syntax with `pyupgrade`_:

.. code:: console

   $ nbqa pyupgrade my_notebook.ipynb --py36-plus --nbqa-mutate
   Rewriting my_notebook.ipynb

Perform static code analysis with `pylint`_:

.. code:: console

   $ nbqa pylint my_notebook.ipynb --disable=C0114
   my_notebook.ipynb:cell_1:5:0: W0611: Unused import datetime (unused-import)

.. _black: https://black.readthedocs.io/en/stable/
.. _isort: https://timothycrosley.github.io/isort/
.. _mypy: http://mypy-lang.org/
.. _doctest: https://docs.python.org/3/library/doctest.html
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _pyupgrade: https://github.com/asottile/pyupgrade
.. _pylint: https://www.pylint.org/
