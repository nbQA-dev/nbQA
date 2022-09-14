---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
substitutions:
  extra_dependencies: bokeh
---

```{code-cell} ipython3
:tags: [skip-flake8]

import os

import glob

import nbqa
```

# Some markdown cell containing \\n

+++ {"tags": ["skip-mdformat"]}

# First level heading

```{code-cell} ipython3
:tags: [flake8-skip]

%%time foo
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

    return 'hello {}'.format(name)


!ls
hello(3)
```

```python
2 +2
```

```{code-cell} ipython3
    %%bash

        pwd
```

```{code-cell} ipython3
from random import randint

if __debug__:
    %time randint(5,10)
```

```{code-cell} ipython3
import pprint
import sys

if __debug__:
    pretty_print_object = pprint.PrettyPrinter(
        indent=4, width=80, stream=sys.stdout, compact=True, depth=5
    )

pretty_print_object.isreadable(["Hello", "World"])
```
