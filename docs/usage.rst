=====
Usage
=====

As command-line tool
--------------------

Just as you would normally run, e.g.

.. code-block::

    flake8 my_python_file.py

, :code:`nbQA` allows you to run

.. code-block::

    nbqa flake8 my_jupyter_notebook.ipynb

. Any extra flags / configuration will be passed on to :code:`nbqa` - so for example, the following is valid:

.. code-block::

    nbqa black my_jupyter_notebook.ipynb --check

.
