<h1 align="center">
	<img
		width="400"
		alt="nbQA"
		src="https://github.com/nbQA-dev/nbQA/raw/master/assets/logo.png">
</h1>

<h3 align="center">
	Run any standard Python code quality tool on a Jupyter Notebook
</h3>

<p align="center">
	<a href="https://github.com/nbQA-dev/nbQA/actions?workflow=tox"><img
		alt="tox"
		src="https://github.com/nbQA-dev/nbQA/workflows/tox/badge.svg"></a>
	<a href="https://codecov.io/gh/nbQA-dev/nbQA"><img
		alt="codecov"
		src="https://codecov.io/gh/nbQA-dev/nbQA/branch/master/graph/badge.svg"></a>
	<a href="https://pypi.org/project/nbqa/"><img
		alt="versions"
		src="https://img.shields.io/pypi/pyversions/nbqa.svg"></a>
	<a href="https://github.com/pre-commit/pre-commit"><img
		alt="pre-commit"
		src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white"></a>
	<a href="https://gitter.im/nbQA/nbQA"><img
		alt="chat"
		src="https://badges.gitter.im/Join%20Chat.svg"></a>
</p>

<p align="center">
    <a href="#readme">
        <img alt="demo" src="https://raw.githubusercontent.com/nbQA-dev/nbQA-demo/master/demo.gif">
    </a>
</p>

# Table of contents

- [Table of contents](#table-of-contents)
  - [🎉 Installation](#-installation)
  - [🚀 Examples](#-examples)
    - [Command-line](#command-line)
    - [Pre-commit](#pre-commit)
  - [🥳 Used by](#-used-by)
  - [💬 Testimonials](#-testimonials)
  - [👥 Contributing](#-contributing)

## 🎉 Installation

In your [virtual environment](https://realpython.com/python-virtual-environments-a-primer/), run one of the following:

- `python -m pip install -U nbqa` (minimal installation)
- `python -m pip install -U nbqa[toolchain]` (install supported code quality tools as well)
- `conda install -c conda-forge nbqa` (if you use conda)

## 🚀 Examples

### Command-line

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

Upgrade your syntax with [pyupgrade](https://github.com/asottile/pyupgrade):

```console
$ nbqa pyupgrade my_notebook.ipynb --py36-plus --nbqa-mutate
Rewriting my_notebook.ipynb
```

See [command-line examples](https://nbqa.readthedocs.io/en/latest/examples.html) for examples involving [pylint](https://www.pylint.org/), [flake8](https://flake8.pycqa.org/en/latest/),
[doctest](https://docs.python.org/3/library/doctest.html), and [mypy](http://mypy-lang.org/).

### Pre-commit

Here's an example of how to set up some pre-commit hooks:

1. Put this in your `pyproject.toml` file (see
[configuration](https://nbqa.readthedocs.io/en/latest/configuration.html)
for details)

   ```toml
   [tool.nbqa.config]
   isort = "setup.cfg"
   black = "pyproject.toml"

   [tool.nbqa.mutate]
   isort = 1
   black = 1
   pyupgrade = 1

   [tool.nbqa.addopts]
   isort = ["--treat-comment-as-code", "# %%"]
   pyupgrade = ["--py36-plus"]
   ```

2. Put this in your `.pre-commit-config.yaml` file (see [usage as pre-commit hook](https://nbqa.readthedocs.io/en/latest/pre-commit.html))

   ```yaml
   - repo: https://github.com/nbQA-dev/nbQA
     rev: 0.3.5
     hooks:
       - id: nbqa-black
       - id: nbqa-pyupgrade
       - id: nbqa-isort
   ```

## 🥳 Used by

Take some inspiration from their config files 😉

- **PyMC3**: [pyproject.toml](https://github.com/pymc-devs/pymc3/blob/master/pyproject.toml) [.pre-commit-config.yaml](https://github.com/pymc-devs/pymc3/blob/master/.pre-commit-config.yaml)
- **pandas-profiling** [.pre-commit-config.yaml](https://github.com/pandas-profiling/pandas-profiling/blob/develop/.pre-commit-config.yaml)
- **alibi** [.pre-commit-config.yaml](https://github.com/SeldonIO/alibi/blob/master/.pre-commit-config.yaml)
- **NLP Profiler**: [pyproject.toml](https://github.com/neomatrix369/nlp_profiler/blob/master/pyproject.toml) [.pre-commit-config.yaml](https://github.com/neomatrix369/nlp_profiler/blob/master/.pre-commit-config.yaml)

## 💬 Testimonials

**Michael Kennedy & Brian Okken**, [hosts of the Python Bytes podcast](https://pythonbytes.fm/)
> This is really cool. I think it brings so much of the code formatting and code analysis, clean up to notebooks, which I think had been really lacking

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
    <td align="center"><a href="https://github.com/ntaylor-nanigans"><img src="https://avatars0.githubusercontent.com/u/44039328?v=4" width="100px;" alt=""/><br /><sub><b>Nat Taylor</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Antaylor-nanigans" title="Bug reports">🐛</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification.
Contributions of any kind welcome!
