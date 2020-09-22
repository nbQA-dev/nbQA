<img src="https://github.com/nbQA-dev/nbQA/raw/master/assets/logo.png" alt="logo" width="400"/>

# nbQA

[![image](https://github.com/nbQA-dev/nbQA/workflows/tox/badge.svg)](https://github.com/nbQA-dev/nbQA/actions?workflow=tox)
[![image](https://codecov.io/gh/nbQA-dev/nbQA/branch/master/graph/badge.svg)](https://codecov.io/gh/nbQA-dev/nbQA)
[![image](https://badge.fury.io/py/nbqa.svg)](https://badge.fury.io/py/nbqa)
[![image](https://readthedocs.org/projects/nbqa/badge/?version=latest&style=plastic)](https://nbqa.readthedocs.io/en/latest/)
[![image](https://img.shields.io/pypi/pyversions/nbqa.svg)](https://pypi.org/project/nbqa/)
[![image](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![image](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![image](https://interrogate.readthedocs.io/en/latest/_static/interrogate_badge.svg)](https://github.com/econchick/interrogate)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![image](https://img.shields.io/badge/pylint-10/10-brightgreen.svg)](https://github.com/PyCQA/pylint)
[![image](https://img.shields.io/pypi/dm/nbqa.svg?label=pypi%20downloads&logo=PyPI&logoColor=white)](https://pypistats.org/packages/nbqa)
[![All Contributors](https://img.shields.io/github/all-contributors/nbQA-dev/nbQA)](#contributors)

<p align="center">
    <a href="#readme">
        <img alt="demo" src="https://raw.githubusercontent.com/nbQA-dev/nbQA-demo/master/demo.gif">
    </a>
</p>

Adapter to run any standard code-quality tool on a Jupyter notebook.
Documentation is hosted [here](https://nbqa.readthedocs.io/en/latest/).

## Installation

Install `nbqa` with [pip](https://pip.pypa.io):

```bash
pip install -U nbqa
```

## Examples

Reformat your notebook with
[black](https://black.readthedocs.io/en/stable/):

```bash
$ nbqa black my_notebook.ipynb --line-length=96 --nbqa-mutate
reformatted my_notebook.ipynb
All done! ✨ 🍰 ✨
1 files reformatted.
```

Sort your imports with [isort](https://timothycrosley.github.io/isort/):

```bash
$ nbqa isort my_notebook.ipynb --treat-comment-as-code '# %%' --nbqa-mutate
Fixing my_notebook.ipynb
```

Check your type annotations with [mypy](http://mypy-lang.org/):

```bash
$ nbqa mypy my_notebook.ipynb --ignore-missing-imports
my_notebook.ipynb:cell_10:5: error: Argument "num1" to "add" has incompatible type "str"; expected "int"
```

Run your docstring tests with
[doctest](https://docs.python.org/3/library/doctest.html):

```bash
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

## Configuration

Here\'s an example `.nbqa.ini` file - see
[configuration](https://nbqa.readthedocs.io/en/latest/configuration.html)
for more on configuration:

```ini
[isort]
config = setup.cfg
mutate = 1
addopts = --treat-comment-as-code '# %%%%'

[flake8]
config = setup.cfg
```

## Usage as pre-commit hook

If you want to use `nbqa` with [pre-commit](https://pre-commit.com/),
here\'s an example of what you could add to your
`.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/nbQA-dev/nbQA
  rev: 0.1.32
  hooks:
    - id: nbqa
      args: ["flake8"]
      name: nbqa-flake8
      alias: nbqa-flake8
      additional_dependencies: ["flake8"]
    - id: nbqa
      args: ["isort", "--nbqa-mutate"]
      name: nbqa-isort
      alias: nbqa-isort
      additional_dependencies: ["isort"]
```

## Supported third party packages

In theory, `nbqa` can adapt any Python code-quality tool to a Jupyter Notebook.

In practice, here are the tools it\'s been tested with:

- [flake8](https://flake8.pycqa.org/en/latest/)
- [black](https://black.readthedocs.io/en/stable/)
- [isort](https://timothycrosley.github.io/isort/)
- [mypy](http://mypy-lang.org/)
- [doctest](https://docs.python.org/3/library/doctest.html)

## Contributing

I will give write-access to anyone who contributes anything useful
(e.g. pull request / bug report) - see the
[contributing guide](https://nbqa.readthedocs.io/en/latest/contributing.html)
for details on how to do so.

## Contributors ✨

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
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
