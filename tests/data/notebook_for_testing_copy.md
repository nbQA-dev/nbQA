---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: "1.3"
      jupytext_version: 1.14.1
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import os

import glob

import nbqa
```

# Some markdown cell containing \n

```python
%%time
def hello(name: str = "world\n"):
    """
    Greet user.

    Examples
    --------
    >>> hello()
    'hello world\\n'
    >>> hello("goodbye")
    'hello goodby'
    """
    if True:
        %time # indented magic!
    return f'hello {name}'


hello(3)
```

```python

```
