Configuration
-------------

You can configure :code:`nbQA` either at the command line, or by using a :code:`setup.cfg` file. We'll see some examples below.

Extra flags
~~~~~~~~~~~

If you wish to pass extra flags (e.g. :code:`--ignore W503` to :code:`flake8`) you can either run

.. code-block:: bash

    nbqa flake8 my_notebook.ipynb --ignore W503

or you can put the following in your :code:`setup.cfg` file

.. code-block:: cfg

    [nbqa.addopts]
    flake8 = --ignore W503

Config file
~~~~~~~~~~~

By default, :code:`nbQA` will use :code:`setup.cfg` to get the configs for your third-party tool.
If you want to use a different config file for your third-party tool (e.g. :code:`.mypy.ini` for :code:`mypy`), you can run

.. code-block:: bash

    nbqa mypy my_notebook.ipynb --nbqa-config .mypy.ini

or you can put the following in your :code:`setup.cfg` file

.. code-block:: cfg

    [nbqa.config]
    mypy = .mypy.ini

Allow mutations
~~~~~~~~~~~~~~~

By default, :code:`nbQA` won't modify your notebooks. If you wish to let your third-party tool modify your notebooks, you can
either pass the :code:`--nbqa-mutate` flag at the command-line, e.g.

.. code-block:: bash

    nbqa black my_notebook.ipynb --nbqa-mutate

or you can put the following in your :code:`setup.cfg` file

.. code-block:: cfg

    [nbqa.mutate]
    black = 1

Ignore cells
~~~~~~~~~~~~

By default, :code:`nbQA` will ignore line magics (e.g. :code:`%matplotlib inline`), and :code:`%%bash` and :code:`%%script` cell magics.
To ignore extra cells, you can use the :code:`--nbqa-ignore-cells` CLI argument, e.g.

.. code-block:: bash

    nbqa black my_notebook.ipynb --nbqa-ignore-cells %%html,%%cython

, or the :code:`ignore_cells` option in your :code:`.nbqa.ini` file, e.g.

.. code-block:: cfg

    [nbqa.ignore_cells]
    black = %%html,%%cython
