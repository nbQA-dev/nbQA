=================
Known limitations
=================

Automagic
~~~~~~~~~

`Automagic <https://ipython.readthedocs.io/en/stable/interactive/magics.html?highlight=automagic#magic-automagic>`_ ("Make magic functions callable without having to type the initial %") will not work well with most code quality tools,
as it will not parse as valid Python syntax.

Linters (flake8, mypy, pylint, ...)
-----------------------------------

Shell magic assignment
~~~~~~~~~~~~~~~~~~~~~~

Assigning to a variable with shell magic will result in it being considered "undefined".

Example:

.. code-block:: ipython

    flake8_version = !pip list 2>&1 | grep flake8

    if flake8_version:
        print(flake8_version)

``Mypy``, ``flake8``, and ``pylint`` will warn about ``'flake8_version'`` being undefined.
