========
Tutorial
========

Welcome! Here's a little tutorial, assuming you're brand-new here. We'll walk you through:

- creating a virtual environment;
- installing ``nbqa``, and checking your installation;
- running ``black`` on your notebook;
- configuring ``nbqa``.

Creating a virtual environment
------------------------------

Rather than using your system installation of Python, we recommend using a virtual environment so that your dependencies don't clash with each other.
Here's one way to set one up using Conda - see `this tutorial <https://realpython.com/python-virtual-environments-a-primer/>`_ for other options.

1. Install the `Miniconda distribution of Python <https://docs.conda.io/en/latest/miniconda.html>`_;
2. Create a new virtual environment. Here, we'll call it ``nbqa-env``

.. code-block:: bash

    conda create -n nbqa-env python=3.8 -y

3. Activate your virtual environment

.. code-block:: bash

    conda activate nbqa-env

Install nbqa and black
----------------------

1. Install ``nbqa`` and at least one Python code quality tool - here, we'll use ``black``

.. code-block:: bash

    pip install -U nbqa black

2. Check your installation

.. code-block:: bash

    nbqa --version
    black --version

Neither of these commands should error.

Run nbqa black
--------------

1. Locate a Jupyter Notebook on your system. If you don't have one, `here <https://www.kaggle.com/startupsci/titanic-data-science-solutions>`_
   is a nice one you can download.

2. Run the ``black`` formatter on your notebook via ``nbqa``

.. code-block:: bash

    nbqa black notebook.ipynb --line-length=96

3. Reload your notebook, and admire the difference!

Configuring nbqa
----------------

Rather than having to type ``--line-length=96`` from the command-line for
each notebook you want to reformat, you can configure ``nbqa`` in your ``pyproject.toml`` file.
Open up your ``pyproject.toml`` file (or create one if you don't have one already) and add in the following lines ::

    [tool.black]
    line-length = 96

Now, you'll be able to run the command from the previous section with just

.. code-block:: bash

    nbqa black notebook.ipynb

Much simpler!

See :ref:`configuration<configuration>` for how to further configure how ``nbqa``.

Writing your own tool
---------------------

You can use ``nbqa`` to run your own custom tool on Jupyter Notebooks too. You just need to make sure you can
run it as a module on a given set of Python files. For example, if your tool is called ``my_amazing_tool``, then
as long as you can run

.. code-block:: bash

    python -m my_amazing_tool file_1.py file_2.py

then you will be able to run

.. code-block:: bash

    nbqa my_amazing_tool notebook_1.ipynb notebook_2.ipynb
