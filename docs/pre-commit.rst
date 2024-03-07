==========
Pre-commit
==========

Usage
-----

You can easily use ``nbqa`` as a `pre-commit <https://pre-commit.com/>`_ hook.

Here's an example of what you could include in your ``.pre-commit-config.yaml`` file:

.. code-block:: yaml

    repos:
    - repo: https://github.com/nbQA-dev/nbQA
      rev: 1.8.4
      hooks:
       - id: nbqa-black
         additional_dependencies: [black==20.8b1]
       - id: nbqa-pyupgrade
         additional_dependencies: [pyupgrade==2.7.3]
       - id: nbqa-isort
         additional_dependencies: [isort==5.6.4]

For best reproducibility, you should pin your dependencies (as above). Running ``pre-commit autoupdate`` will update your hooks' versions, but
versions of additional dependencies need to be updated manually.

See `.pre-commit-hooks.yaml <https://github.com/nbQA-dev/nbQA/blob/master/.pre-commit-hooks.yaml>`_ for all available built-in hooks.

Custom hooks
------------

If you have your own custom tool (e.g. ``customtool``) for which we currently don't have a built-in hook, you can define your own one with:

.. code-block:: yaml

    - repo: https://github.com/nbQA-dev/nbQA
      rev: 1.8.4
      hooks:
        - id: nbqa
          entry: nbqa customtool
          name: nbqa-customtool
          alias: nbqa-customtool
          additional_dependencies: [customtool==<version number>]

If there are additional Python code quality tools you would like us to make a hook for, please :ref:`open a pull request<contributing>`
or let us know in the `issue tracker <https://github.com/nbQA-dev/nbQA/issues>`_!

Configuration
-------------

To pass command line arguments, use the `pre-commit args <https://pre-commit.com/#config-args>`_ option:

.. code-block:: yaml

    repos:
    - repo: https://github.com/nbQA-dev/nbQA
      rev: 1.8.4
      hooks:
       - id: nbqa-pyupgrade
         args: [--py38-plus]
       - id: nbqa-isort
         args: [--profile=black]
       - id: nbqa-flake8
         args: [--ignore=E402] # E402 module level import not at top of file

Note that some tools like ``flake8`` require the flag and its value to be joined by an equal sign in order to not interpret the value as a
filename (`GH issue <https://github.com/nbQA-dev/nbQA/issues/731>`_).

See :ref:`configuration<configuration>` for how to further configure how ``nbqa`` should run each tool. Also, see the `pre-commit documentation <https://pre-commit.com/>`_
for how to further configure these hooks.

Temporarily disable hooks
-------------------------

Although not recommended, it is still possible to temporarily **disable all checks**
using ``git commit --no-verify``, or **just specific ones** using the ``SKIP``
environment variable. For example, on a Unix-like operating system:

.. code:: bash

    SKIP=nbqa-black git commit -m "foo"


For more details, please check out
`the pre-commit documentation <https://pre-commit.com/#temporarily-disabling-hooks>`_.
