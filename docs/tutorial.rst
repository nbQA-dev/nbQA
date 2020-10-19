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
2. Create a new virtual environment. Here, we'll call it ``nbqa-env`` ::

    conda create -n nbqa-env python=3.8 -y

3. Activate your virtual environment ::

    conda activate nbqa-env

Install nbqa and black
----------------------

1. Install ``nbqa`` and at least one Python code quality tool - here, we'll use ``black`` ::

    pip install -U nbqa black

2. Check your installation ::

    nbqa --version
    black --version

Neither of these commands should error.

Run nbqa black
--------------

1. Locate a Jupyter Notebook on your system. If you don't have one, `here <https://www.kaggle.com/startupsci/titanic-data-science-solutions>`_
   is a nice one you can download.

2. Run the ``black`` formatter on your notebook via ``nbqa`` ::

    nbqa black notebook.ipynb --nbqa-mutate --line-length=96

3. Reload your notebook, and admire the difference!

Configuring nbqa
----------------

Rather than having to type ``--nbqa-mutate --line-length=96`` from the command-line for
each notebook you want to reformat, you can configure ``nbqa`` in your ``pyproject.toml`` file.
Open up your ``pyproject.toml`` file (or create one if you don't have one already) and add in the following lines ::

    [tool.black]
    line-length = 96

    [tool.nbqa.config]
    black = "pyproject.toml"

    [tool.nbqa.mutate]
    black = 1

Now, you'll be able to run the command from the previous section with just ::

    nbqa black notebook.ipynb

Much simpler!

See :ref:`configuration<configuration>` for how to further configure how ``nbqa``.
