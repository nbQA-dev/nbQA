=================
Known limitations
=================

Black
-----

Comment after trailing comma
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Putting a comment after a trailing comma will make **Black** move the comment to the
next line.

Example:

.. code:: python

    plt.plot();  # some comment


Will be transformed to:

.. code:: python

    plt.plot()
    # some comment

You can overcome this limitation by moving the comment to the previous line:

.. code:: python

    # some comment
    plt.plot();
