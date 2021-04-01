.. _configuration:

Configuration
-------------

You can configure :code:`nbQA` either at the command line, or by using a :code:`pyproject.toml` file. We'll see some examples below.

Extra flags
~~~~~~~~~~~

If you wish to pass extra flags (e.g. :code:`--extend-ignore E203` to :code:`flake8`) you can either run

.. code-block:: bash

    nbqa flake8 my_notebook.ipynb --extend-ignore E203

or you can put the following in your :code:`pyproject.toml` file

.. code-block:: toml

    [tool.nbqa.addopts]
    flake8 = [
        "--extend-ignore=E203"
    ]

Config file
~~~~~~~~~~~

By default, :code:`nbQA` will look up the configuration of the third party tool in the following files :code:`setup.cfg`, :code:`tox.ini` and :code:`pyproject.toml`.
If you want to use a different config file for your third-party tool (e.g. :code:`.mypy.ini` for :code:`mypy`), you can run

.. code-block:: bash

    nbqa mypy my_notebook.ipynb --nbqa-config .mypy.ini

or you can put the following in your :code:`pyproject.toml` file

.. code-block:: toml

    [tool.nbqa.config]
    mypy = ".mypy.ini"

Allow mutations
~~~~~~~~~~~~~~~

By default, :code:`nbQA` won't modify your notebooks. If you wish to let your third-party tool modify your notebooks, you can
either pass the :code:`--nbqa-mutate` flag at the command-line, e.g.

.. code-block:: bash

    nbqa black my_notebook.ipynb --nbqa-mutate

or you can put the following in your :code:`pyproject.toml` file

.. code-block:: toml

    [tool.nbqa.mutate]
    black = 1

.. note::
    If you let :code:`nbQA` mutate your notebook, then trailing newlines will be removed from cells.

Ignore cells
~~~~~~~~~~~~

By default, :code:`nbQA` will ignore line magics (e.g. :code:`%matplotlib inline`), and :code:`%%bash` and :code:`%%script` cell magics.
To ignore extra cells, you can use the :code:`--nbqa-ignore-cells` CLI argument, e.g.

.. code-block:: bash

    nbqa black my_notebook.ipynb --nbqa-ignore-cells %%html,%%cython

or the :code:`process_cells` option in your :code:`pyproject.toml` file, e.g.

.. code-block:: toml

    [tool.nbqa.process_cells]
    black = "%%html,%%cython"

Include / exclude
~~~~~~~~~~~~~~~~~

To include or exclude notebooks from being processed, we recommend using ``nbQA``'s own ``--nbqa-files`` and ``--nbqa-exclude`` flags.
These take regex patterns and match posix-like paths, `exactly like the same options from pre-commit <https://pre-commit.com/#regular-expressions>`_.
These can be set from the command-line with the ``--nbqa-files`` and ``--nbqa-exclude`` flags, or in your ``.pyproject.toml`` file in the
``[tool.nbqa.files]`` and ``[tool.nbqa.exclude]`` sections.

Say you're running ``nbqa isort`` on a directory ``my_directory``. Here are some examples of how to include/exclude files:

- exclude notebooks in ``my_directory`` whose name starts with ``poc_``:

    .. code-block:: toml

        [tool.nbqa.exclude]
        isort = "^my_directory/poc_"

- exclude notebooks in subdirectory ``my_directory/my_subdirectory``:

    .. code-block:: toml

        [tool.nbqa.exclude]
        isort = "^my_directory/my_subdirectory/"

- only include notebooks in ``my_directory`` whose name starts with ``EDA``:

    .. code-block:: toml

        [tool.nbqa.files]
        isort = "^my_directory/EDA"

All the above examples can equivalently be run from the command-line, e.g. as

.. code-block:: bash

    nbqa isort my_directory --nbqa-exclude ^my_directory/poc_
