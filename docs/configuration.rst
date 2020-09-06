Configuration
-------------

You can configure :code:`nbQA` either at the command line, or by using a :code:`.nbqa.ini` file. We'll see some examples below.

Extra flags
~~~~~~~~~~~

If you wish to pass extra flags (e.g. :code:`--ignore W503` to :code:`flake8`) you can either run

.. code-block:: bash

    nbqa flake8 my_notebook.ipynb --ignore W503

or you can put the following in your :code:`.nbqa.ini` file

.. code-block:: ini

    [flake8]
    addopts = --ignore W503

Config file
~~~~~~~~~~~

If you already have a config file for your third-party tool (e.g. :code:`.mypy.ini` for :code:`mypy`), you can run

.. code-block:: bash

    nbqa mypy my_notebook.ipynb --nbqa-config .mypy.ini

or you can put the following in your :code:`.nbqa.ini` file

.. code-block:: ini

    [mypy]
    config = .mypy.ini

Allow mutations
~~~~~~~~~~~~~~~

By default, :code:`nbQA` won't modify your notebooks. If you wish to let your third-party tool modify your notebooks, you can
either pass the :code:`--nbqa-mutate` flag at the command-line, e.g.

.. code-block:: bash

    nbqa black my_notebook.ipynb --nbqa-mutate

or you can put the following in your :code:`.nbqa.ini` file

.. code-block:: ini

    [black]
    mutate = 1
