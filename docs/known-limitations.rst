=================
Known limitations
=================

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

flake8 (and other linters)
--------------------------

Line magics
~~~~~~~~~~~

If you import a module and then *only* use it in a line magic, then you may get an "unused import"
warning from ``flake8``.

Example:

.. code:: python

    # cell 1
    import numpy as np

    # cell 2
    %time np.random.randn(1000)

You can overcome this limitation by using a cell magic to time execution:

.. code:: python

    # cell 1
    import numpy as np

    # cell 2
    %%time
    np.random.randn(1000)
