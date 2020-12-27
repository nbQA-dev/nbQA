=================
Known limitations
=================

Automagic
~~~~~~~~~

`Automagic <https://ipython.readthedocs.io/en/stable/interactive/magics.html?highlight=automagic#magic-automagic>`_ ("Make magic functions callable without having to type the initial %") will not work well with most code quality tools,
as it will not parse as valid Python syntax.

Black
-----

Comment after trailing semicolon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Putting a comment after a trailing semicolon will make ``black`` move the comment to the
next line, and the semicolon will be lost.

Example:

.. code:: python

    plt.plot();  # some comment


Will be transformed to:

.. code:: python

    plt.plot()
    # some comment

You can overcome this limitation by moving the comment to the previous line - like this,
the trailing semicolon will be preserved:

.. code:: python

    # some comment
    plt.plot();

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
