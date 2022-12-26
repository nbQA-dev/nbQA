# %%NBQA-CELL-SEPc5fc8b


# %%NBQA-CELL-SEPc5fc8b
# CELL MAGIC 0x2B4D8329
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

    return f"hello {name}"


hash(0xF83024A0)
hello(3)


# %%NBQA-CELL-SEPc5fc8b

if __debug__:
    hash(0x9BD26189)


# %%NBQA-CELL-SEPc5fc8b
import pprint
import sys

if __debug__:
    pretty_print_object = pprint.PrettyPrinter(
        indent=4, width=80, stream=sys.stdout, compact=True, depth=5
    )

pretty_print_object.isreadable(["Hello", "World"])
