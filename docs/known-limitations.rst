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
