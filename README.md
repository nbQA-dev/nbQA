<img src="https://github.com/nbQA-dev/nbQA/raw/master/assets/logo.png" alt="logo" width="400"/>

# nbQA

[![image](https://github.com/nbQA-dev/nbQA/workflows/tox/badge.svg)](https://github.com/nbQA-dev/nbQA/actions?workflow=tox)
[![image](https://codecov.io/gh/nbQA-dev/nbQA/branch/master/graph/badge.svg)](https://codecov.io/gh/nbQA-dev/nbQA)
[![image](https://readthedocs.org/projects/nbqa/badge/?version=latest)](https://nbqa.readthedocs.io/en/latest/)
[![image](https://img.shields.io/pypi/pyversions/nbqa.svg)](https://pypi.org/project/nbqa/)
[![image](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![image](https://img.shields.io/pypi/dm/nbqa.svg?label=pypi%20downloads&logo=PyPI&logoColor=white)](https://pypistats.org/packages/nbqa)
[![image](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/nbQA/nbQA)

<p align="center">
    <a href="#readme">
        <img alt="demo" src="https://raw.githubusercontent.com/nbQA-dev/nbQA-demo/master/demo.gif">
    </a>
</p>

A tool (and pre-commit hook) to run any standard Python code-quality tool on a Jupyter notebook.

## 🎉 Installation

Install `nbqa` in your [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) with [pip](https://pip.pypa.io):

```bash
python -m pip install -U nbqa
```

## 🚀 Examples

Reformat your notebooks with
[black](https://black.readthedocs.io/en/stable/):

```console
$ nbqa black my_notebook.ipynb --nbqa-mutate
reformatted my_notebook.ipynb
All done! ✨ 🍰 ✨
1 files reformatted.
```

Sort your imports with [isort](https://timothycrosley.github.io/isort/):

```console
$ nbqa isort my_notebook.ipynb --treat-comment-as-code '# %%' --nbqa-mutate
Fixing my_notebook.ipynb
```

Check your type annotations with [mypy](http://mypy-lang.org/):

```console
$ nbqa mypy my_notebook.ipynb --ignore-missing-imports
my_notebook.ipynb:cell_10:5: error: Argument "num1" to "add" has incompatible type "str"; expected "int"
```

Run your docstring tests with
[doctest](https://docs.python.org/3/library/doctest.html):

```console
$ nbqa doctest my_notebook.ipynb
**********************************************************************
File "my_notebook.ipynb", cell_2:11, in my_notebook.add
Failed example:
    add(2, 2)
Expected:
    4
Got:
    5
**********************************************************************
1 items had failures:
1 of   2 in my_notebook.hello
***Test Failed*** 1 failures.
```

Check for style guide enforcement with [flake8](https://flake8.pycqa.org/en/latest/):

```console
$ nbqa flake8 my_notebook.ipynb --extend-ignore=E203,E302,E305,E703
my_notebook.ipynb:cell_3:1:1: F401 'import pandas as pd' imported but unused
```

Upgrade your syntax with [pyupgrade](https://github.com/asottile/pyupgrade):

```console
$ nbqa pyupgrade my_notebook.ipynb --py36-plus --nbqa-mutate
Rewriting my_notebook.ipynb
```

Perform static code analysis with [pylint](https://www.pylint.org/):

```console
$ nbqa pylint my_notebook.ipynb --disable=C0114
my_notebook.ipynb:cell_1:5:0: W0611: Unused import datetime (unused-import)
```

## 🔧 Configuration

You can configure `nbqa` either at the command line, or by using a `pyproject.toml` file - see
[configuration](https://nbqa.readthedocs.io/en/latest/configuration.html)
for details and examples.

## 👷 Pre-commit

See [usage as pre-commit hook](https://nbqa.readthedocs.io/en/latest/pre-commit.html) for examples.

## 💬 Testimonials

**Alex Andorra**,
[Data Scientist, ArviZ & PyMC Dev, Host of 'Learning Bayesian Statistics' Podcast 🎙️](https://learnbayesstats.anvil.app/):

> well done on `nbqa` @MarcoGorelli ! Will be super useful in CI 😉

**Girish Pasupathy**,
[Software engineer and now core-contributor](https://github.com/girip11):

> thanks a lot for your effort to create such a useful tool

## 👥 Contributing

I will give write-access to anyone who contributes anything useful
(e.g. pull request / bug report) - see the
[contributing guide](https://nbqa.readthedocs.io/en/latest/contributing.html)
for details on how to do so.

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/MarcoGorelli"><img src="https://avatars2.githubusercontent.com/u/33491632?v=4" width="100px;" alt=""/><br /><sub><b>Marco Gorelli</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=MarcoGorelli" title="Code">💻</a> <a href="#maintenance-MarcoGorelli" title="Maintenance">🚧</a> <a href="https://github.com/nbQA-dev/nbQA/pulls?q=is%3Apr+reviewed-by%3AMarcoGorelli" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=MarcoGorelli" title="Tests">⚠️</a> <a href="#ideas-MarcoGorelli" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/s-weigand"><img src="https://avatars2.githubusercontent.com/u/9513634?v=4" width="100px;" alt=""/><br /><sub><b>Sebastian Weigand</b></sub></a><br /><a href="#tool-s-weigand" title="Tools">🔧</a> <a href="https://github.com/nbQA-dev/nbQA/pulls?q=is%3Apr+reviewed-by%3As-weigand" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=s-weigand" title="Documentation">📖</a> <a href="#ideas-s-weigand" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/girip11"><img src="https://avatars1.githubusercontent.com/u/5471162?v=4" width="100px;" alt=""/><br /><sub><b>Girish Pasupathy</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=girip11" title="Code">💻</a> <a href="#infra-girip11" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Agirip11" title="Bug reports">🐛</a> <a href="https://github.com/nbQA-dev/nbQA/pulls?q=is%3Apr+reviewed-by%3Agirip11" title="Reviewed Pull Requests">👀</a> <a href="#ideas-girip11" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/fcatus"><img src="https://avatars0.githubusercontent.com/u/56323389?v=4" width="100px;" alt=""/><br /><sub><b>fcatus</b></sub></a><br /><a href="#infra-fcatus" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    <td align="center"><a href="https://github.com/HD23me"><img src="https://avatars3.githubusercontent.com/u/68745664?v=4" width="100px;" alt=""/><br /><sub><b>HD23me</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3AHD23me" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://neomatrix369.wordpress.com/about"><img src="https://avatars0.githubusercontent.com/u/1570917?v=4" width="100px;" alt=""/><br /><sub><b>mani</b></sub></a><br /><a href="#ideas-neomatrix369" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-neomatrix369" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    <td align="center"><a href="https://orcid.org/0000-0001-9488-1870"><img src="https://avatars3.githubusercontent.com/u/465923?v=4" width="100px;" alt=""/><br /><sub><b>Daniel Mietchen</b></sub></a><br /><a href="#ideas-Daniel-Mietchen" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://gacka.space/"><img src="https://avatars1.githubusercontent.com/u/25684390?v=4" width="100px;" alt=""/><br /><sub><b>Michał Gacka</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Am3h0w" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/HappyFacade"><img src="https://avatars0.githubusercontent.com/u/54226355?v=4" width="100px;" alt=""/><br /><sub><b>Happy</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=HappyFacade" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification.
Contributions of any kind welcome!
