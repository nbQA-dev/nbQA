<h1 align="center">
	<img
		width="400"
		alt="nbQA"
		src="https://github.com/nbQA-dev/nbQA-demo/raw/master/assets/logo.png">
</h1>

<h3 align="center">
	Run isort, pyupgrade, mypy, pylint, flake8, mdformat, black, blacken-docs, and more on Jupyter Notebooks
</h3>

<p align="center">
	<a href="https://github.com/nbQA-dev/nbQA/actions?workflow=tox"><img
		alt="tox"
		src="https://github.com/nbQA-dev/nbQA/workflows/tox/badge.svg"></a>
	<a href="https://codecov.io/gh/nbQA-dev/nbQA"><img
		alt="codecov"
		src="https://codecov.io/gh/nbQA-dev/nbQA/branch/master/graph/badge.svg"></a>
	<a href="https://results.pre-commit.ci/latest/github/nbQA-dev/nbQA/master"><img
		alt="pre-commit"
		src="https://results.pre-commit.ci/badge/github/nbQA-dev/nbQA/master.svg"></a>
</p>

<p align="center">
	<a href="https://pypi.org/project/nbqa/"><img
		alt="versions"
		src="https://img.shields.io/pypi/pyversions/nbqa.svg"></a>
	<a href="https://gitter.im/nbQA/nbQA"><img
		alt="chat"
		src="https://badges.gitter.im/Join%20Chat.svg"></a>
	<a href="https://nbqa.readthedocs.io/en/latest/"><img
		alt="docs"
		src="https://readthedocs.org/projects/nbqa/badge/?version=latest"></a>
</p>

<p align="center">
	<a href="https://pepy.tech/project/nbqa"><img
		alt="downloads"
		src="https://pepy.tech/badge/nbqa"></a>
</p>

<p align="center">
    <a href="#readme">
        <img alt="demo" src="https://raw.githubusercontent.com/nbQA-dev/nbQA-demo/master/demo.gif">
    </a>
</p>

- ✅ handles IPython magics robustly
- ✅ respects your config files
- ✅ preserves "quiet mode" trailing semicolons
- ✅ lints both code and markdown cells

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

In your [virtual environment](https://realpython.com/python-virtual-environments-a-primer/), run (note: the `$` is not part of the command):

```console
$ python -m pip install -U nbqa
```

## 🚀 Examples

### Command-line

Reformat your notebooks with
[black](https://black.readthedocs.io/en/stable/):

```console
$ nbqa black my_notebook.ipynb
reformatted my_notebook.ipynb
All done! ✨ 🍰 ✨
1 files reformatted.
```

Sort your imports with [isort](https://timothycrosley.github.io/isort/):

```console
$ nbqa isort my_notebook.ipynb
Fixing my_notebook.ipynb
```

Upgrade your syntax with [pyupgrade](https://github.com/asottile/pyupgrade):

```console
$ nbqa pyupgrade my_notebook.ipynb --py36-plus
Rewriting my_notebook.ipynb
```

Format your markdown cells with [mdformat](https://mdformat.readthedocs.io/en/stable/index.html):

```console
$ nbqa mdformat my_notebook.ipynb --nbqa-md --nbqa-diff
Cell 2
------
--- my_notebook.ipynb
+++ my_notebook.ipynb
@@ -1,2 +1 @@
-First level heading
-===
+# First level heading

To apply these changes, remove the `--nbqa-diff` flag
```

See [command-line examples](https://nbqa.readthedocs.io/en/latest/examples.html) for examples involving [doctest](https://docs.python.org/3/library/doctest.html), [flake8](https://flake8.pycqa.org/en/latest/), [mypy](http://mypy-lang.org/), [pylint](https://www.pylint.org/), [autopep8](https://github.com/hhatto/autopep8), [pydocstyle](http://www.pydocstyle.org/en/stable/), and [yapf](https://github.com/google/yapf).

### Pre-commit

Here's an example of how to set up some pre-commit hooks: put this in your `.pre-commit-config.yaml` file (see [usage as pre-commit hook](https://nbqa.readthedocs.io/en/latest/pre-commit.html))

```yaml
- repo: https://github.com/nbQA-dev/nbQA
  rev: 1.2.0
  hooks:
    - id: nbqa-black
    - id: nbqa-pyupgrade
      args: [--py36-plus]
    - id: nbqa-isort
```

If you need to select specific versions of any of these linters/formatters,
add them to [`additional_dependencies`](http://pre-commit.com/#pre-commit-configyaml---hooks).

## 🥳 Used by

<details>
<summary>Click here for (non-exhaustive) list of repos</summary>

- https://github.com/ComPWA/ampform
- https://github.com/ComPWA/tensorwaves
- https://github.com/DataS-DHSC/os-maps-example
- https://github.com/Eazhi/World-Happiness-Analysis
- https://github.com/GoogleCloudPlatform/ai-platform-samples
- https://github.com/MRCIEU/epigraphdb
- https://github.com/OpenMined/PyDP
- https://github.com/PlasmaPy/PlasmaPy
- https://github.com/ProjectPythia/pythia-foundations
- https://github.com/SeldonIO/alibi
- https://github.com/TeoZosa/deep-learning-v2-pytorch
- https://github.com/WM-SEMERU/mlproj_template
- https://github.com/alan-turing-institute/sktime
- https://github.com/amor71/LiuAlgoTrader
- https://github.com/bbernst/base_envs
- https://github.com/cheginit/HyRiver-examples
- https://github.com/cheginit/pygeohydro
- https://github.com/cheginit/pynhd
- https://github.com/covid-19-impact-lab/sid-germany
- https://github.com/covid-19-impact-lab/sid
- https://github.com/dapperfu/Python-Simulink
- https://github.com/deepcharles/ruptures
- https://github.com/dhassault/cyclegan_pytorch
- https://github.com/gboeing/osmnx
- https://github.com/glotzerlab/freud-examples
- https://github.com/glotzerlab/hoomd-examples
- https://github.com/glotzerlab/signac-docs
- https://github.com/glotzerlab/signac-examples
- https://github.com/grapl-security/grapl
- https://github.com/hainegroup/oceanspy
- https://github.com/henryiii/python-compiled-minicourse
- https://github.com/intake/intake-esm
- https://github.com/jameslamb/lightgbm-dask-testing
- https://github.com/jdb78/pytorch-forecasting
- https://github.com/jhrcook/advent-of-code_2020
- https://github.com/julian-west/asset_price_correlations
- https://github.com/kratsg/drstorage
- https://github.com/madebr/pyOpt
- https://github.com/matthewfeickert/heputils
- https://github.com/matyama/deep-rl-hands-on
- https://github.com/mayou36/raredecay
- https://github.com/neomatrix369/nlp_profiler
- https://github.com/openforcefield/openff-system
- https://github.com/pandas-profiling/pandas-profiling
- https://github.com/paw-lu/dotfiles
- https://github.com/pawamoy/wps-light
- https://github.com/phinate/clarinet
- https://github.com/pik-primap/climate_categories
- https://github.com/pik-primap/primap2
- https://github.com/pik-primap/unfccc_di_api
- https://github.com/pymc-devs/pymc-examples
- https://github.com/pymc-devs/resources
- https://github.com/saturncloud/examples
- https://github.com/scikit-hep/boost-histogram
- https://github.com/scikit-hep/iminuit
- https://github.com/scikit-hep/mplhep
- https://github.com/scikit-hep/pyhf
- https://github.com/scikit-hep/pylhe
- https://github.com/v-goncharenko/data-science-template
- https://github.com/wemake-services/wemake-python-styleguide
- https://github.com/zfit/phasespace
- https://github.com/zfit/zfit
- https://github.com/zfit/zfit-physics
- https://github.com/zfit/zfit-tutorials

</details>

Is your project missing? Let us know, or open a pull request!

## 💬 Testimonials

**Michael Kennedy & Brian Okken**, [hosts of the Python Bytes podcast](https://pythonbytes.fm/episodes/show/204/take-the-psf-survey-and-will-carlton-drop-by):

> This is really cool. I think it brings so much of the code formatting and code analysis, clean up to notebooks, which I think had been really lacking

**Nikita Sobolev**, [CTO at wemake.services](https://github.com/nbQA-dev/nbQA/issues/386#issuecomment-718046313):

> It is amazing!

**Alex Andorra**,
[Data Scientist, ArviZ & PyMC Dev, Host of 'Learning Bayesian Statistics' Podcast](https://github.com/pymc-devs/pymc3/pull/4074#pullrequestreview-482589774):

> well done on `nbqa` @MarcoGorelli ! Will be super useful in CI

**Matthew Feickert**,
[Postdoc at University of Illinois working on LHC physics](https://twitter.com/HEPfeickert/status/1324823925898027008):

> nbqa in your pre-commit hooks along with @codewithanthony 's pre-commit CI service is amazing!
Everyone using Jupyter notebooks should be doing this.

**Girish Pasupathy**,
[Software engineer and now core-contributor](https://github.com/nbQA-dev/nbQA/issues/164#issuecomment-674529528):

> thanks a lot for your effort to create such a useful tool

**Simon Brugman**, [Data scientist & pandas-profiling dev](https://github.com/nbQA-dev/nbQA/pull/490):

> nbQA helps us to keep notebooks to the same standards as the rest of the code. If you're serious about your code standards, you should keep them consistent across both notebooks and python scripts. Great addition to the ecosystem, thanks!

**Bradley Dice**, [PhD Candidate in Physics & Scientific Computing](https://github.com/nbQA-dev/nbQA/pull/547#issuecomment-786186156):

> nbqa is a clean, easy to use, and effective tool for notebook code style. Formatting and readability makes a huge difference when rendering notebooks in a project's documentation!

**James Lamb**, [engineer @saturn_cloud, LightGBM maintainer](https://twitter.com/_jameslamb/status/1346537148913221634)

> today I learned about `nbqa`, a command-line tool to run linters like `flake8` over #Python code in @ProjectJupyter notebooks. Thanks to @jayyqi for pointing me to it. So far, I really really like it.

**Lars Yencken**, [Tech Lead @ Our World In Data](https://twitter.com/larsyencken/status/1398171287974039553)

> Super useful! I only wish it was built-in to Jupyterlab.

**Vincent D. Warmerdam**, [maintainer @ calmcode.io](https://calmcode.io/shorts/nbqa.html)

> Nice. nbQA looks like a great way to prevent the Untitled12.ipynb-phenomenon. I like!

## 👥 Contributing

I will give write-access to anyone who makes a useful pull request - see the
[contributing guide](https://nbqa.readthedocs.io/en/latest/contributing.html)
for details on how to do so.

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/MarcoGorelli"><img src="https://avatars2.githubusercontent.com/u/33491632?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Marco Gorelli</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=MarcoGorelli" title="Code">💻</a> <a href="#maintenance-MarcoGorelli" title="Maintenance">🚧</a> <a href="https://github.com/nbQA-dev/nbQA/pulls?q=is%3Apr+reviewed-by%3AMarcoGorelli" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=MarcoGorelli" title="Tests">⚠️</a> <a href="#ideas-MarcoGorelli" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/s-weigand"><img src="https://avatars2.githubusercontent.com/u/9513634?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Sebastian Weigand</b></sub></a><br /><a href="#tool-s-weigand" title="Tools">🔧</a> <a href="https://github.com/nbQA-dev/nbQA/pulls?q=is%3Apr+reviewed-by%3As-weigand" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=s-weigand" title="Documentation">📖</a> <a href="#ideas-s-weigand" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/girip11"><img src="https://avatars1.githubusercontent.com/u/5471162?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Girish Pasupathy</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=girip11" title="Code">💻</a> <a href="#infra-girip11" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Agirip11" title="Bug reports">🐛</a> <a href="https://github.com/nbQA-dev/nbQA/pulls?q=is%3Apr+reviewed-by%3Agirip11" title="Reviewed Pull Requests">👀</a> <a href="#ideas-girip11" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/fcatus"><img src="https://avatars0.githubusercontent.com/u/56323389?v=4?s=100" width="100px;" alt=""/><br /><sub><b>fcatus</b></sub></a><br /><a href="#infra-fcatus" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    <td align="center"><a href="https://github.com/HD23me"><img src="https://avatars3.githubusercontent.com/u/68745664?v=4?s=100" width="100px;" alt=""/><br /><sub><b>HD23me</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3AHD23me" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://neomatrix369.wordpress.com/about"><img src="https://avatars0.githubusercontent.com/u/1570917?v=4?s=100" width="100px;" alt=""/><br /><sub><b>mani</b></sub></a><br /><a href="#ideas-neomatrix369" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-neomatrix369" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    <td align="center"><a href="https://orcid.org/0000-0001-9488-1870"><img src="https://avatars3.githubusercontent.com/u/465923?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Daniel Mietchen</b></sub></a><br /><a href="#ideas-Daniel-Mietchen" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://gacka.space/"><img src="https://avatars1.githubusercontent.com/u/25684390?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Michał Gacka</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Am3h0w" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/HappyFacade"><img src="https://avatars0.githubusercontent.com/u/54226355?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Happy</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=HappyFacade" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/ntaylor-nanigans"><img src="https://avatars0.githubusercontent.com/u/44039328?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nat Taylor</b></sub></a><br /><a href="#ideas-ntaylor-nanigans" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=ntaylor-nanigans" title="Code">💻</a> <a href="#tool-ntaylor-nanigans" title="Tools">🔧</a> <a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Antaylor-nanigans" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://caioariede.github.io/"><img src="https://avatars0.githubusercontent.com/u/55533?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Caio Ariede</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=caioariede" title="Documentation">📖</a></td>
    <td align="center"><a href="https://sobolevn.me"><img src="https://avatars1.githubusercontent.com/u/4660275?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nikita Sobolev</b></sub></a><br /><a href="#ideas-sobolevn" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Asobolevn" title="Bug reports">🐛</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=sobolevn" title="Documentation">📖</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/amichayoren/"><img src="https://avatars1.githubusercontent.com/u/48661380?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Amichay Oren</b></sub></a><br /><a href="#ideas-amor71" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/pylang"><img src="https://avatars0.githubusercontent.com/u/10778668?v=4?s=100" width="100px;" alt=""/><br /><sub><b>pylang</b></sub></a><br /><a href="#ideas-pylang" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
  <tr>
    <td align="center"><a href="http://iscinumpy.gitlab.io"><img src="https://avatars1.githubusercontent.com/u/4616906?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Henry Schreiner</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Ahenryiii" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://www.linkedin.com/in/kaiqidong"><img src="https://avatars0.githubusercontent.com/u/9269816?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Kaiqi Dong</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=charlesdong1991" title="Documentation">📖</a></td>
    <td align="center"><a href="http://simonbrugman.nl"><img src="https://avatars2.githubusercontent.com/u/9756388?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Simon Brugman</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Asbrugman" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://coefficient.ai"><img src="https://avatars2.githubusercontent.com/u/2884159?v=4?s=100" width="100px;" alt=""/><br /><sub><b>John Sandall</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Ajohn-sandall" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://nathancooper.io"><img src="https://avatars0.githubusercontent.com/u/7613470?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nathan Cooper</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Ancoop57" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/agruenberger"><img src="https://avatars.githubusercontent.com/u/30429454?v=4?s=100" width="100px;" alt=""/><br /><sub><b>agruenberger</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Aagruenberger" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/ravwojdyla"><img src="https://avatars.githubusercontent.com/u/1419010?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Rafal Wojdyla</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Aravwojdyla" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://bradleydice.com"><img src="https://avatars.githubusercontent.com/u/3943761?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Bradley Dice</b></sub></a><br /><a href="#ideas-bdice" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=bdice" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/ivanmkc"><img src="https://avatars.githubusercontent.com/u/1586049?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ivan Cheung</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Aivanmkc" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://blog.ouseful.info"><img src="https://avatars.githubusercontent.com/u/82988?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Tony Hirst</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/issues?q=author%3Apsychemedia" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/hukkin"><img src="https://avatars.githubusercontent.com/u/3275109?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Taneli Hukkinen</b></sub></a><br /><a href="#maintenance-hukkin" title="Maintenance">🚧</a></td>
    <td align="center"><a href="http://tcbegley.com"><img src="https://avatars.githubusercontent.com/u/15220906?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Tom Begley</b></sub></a><br /><a href="#ideas-tcbegley" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=tcbegley" title="Code">💻</a> <a href="https://github.com/nbQA-dev/nbQA/commits?author=tcbegley" title="Documentation">📖</a></td>
    <td align="center"><a href="https://stevendemartini.bandcamp.com/"><img src="https://avatars.githubusercontent.com/u/1647130?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Steven DeMartini</b></sub></a><br /><a href="https://github.com/nbQA-dev/nbQA/commits?author=sjdemartini" title="Documentation">📖</a></td>
    <td align="center"><a href="https://koaning.io"><img src="https://avatars.githubusercontent.com/u/1019791?v=4?s=100" width="100px;" alt=""/><br /><sub><b>vincent d warmerdam </b></sub></a><br /><a href="#tutorial-koaning" title="Tutorials">✅</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification.
Contributions of any kind welcome!
