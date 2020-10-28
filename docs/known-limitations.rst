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


Will be transformed in:

.. code:: python

    plt.plot()
    # some comment
