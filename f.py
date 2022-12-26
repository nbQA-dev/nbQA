# %%NBQA-CELL-SEP008e8c
import os

import glob

import nbqa


# %%NBQA-CELL-SEP008e8c
# CELL MAGIC 0xC0A3FA93
def hello(name: str = "world\n"):
    """
    Greet user.

    Examples
    --------
    >>> hello()
    'hello world\\n'

    >>> hello("goodbye")
    'hello goodbye'
    """

    return "hello {}".format(name)


hash(0xAAF157B0)
hello(3)


# %%NBQA-CELL-SEP008e8c
from random import randint

if __debug__:
    hash(0xB9CE82A)


# %%NBQA-CELL-SEP008e8c
import pprint
import sys

if __debug__:
    pretty_print_object = pprint.PrettyPrinter(
        indent=4, width=80, stream=sys.stdout, compact=True, depth=5
    )

pretty_print_object.isreadable(["Hello", "World"])
