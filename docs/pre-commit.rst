==========
Pre-commit
==========

Usage
-----

You can easily use ``nbqa`` as a `pre-commit <https://pre-commit.com/>`_ hook.

Here's an example of what you could include in your ``.pre-commit-config.yaml`` file: ::

    repos:
    - repo: https://github.com/nbQA-dev/nbQA
      rev: 0.3.6
      hooks:
        - id: nbqa-black
        - id: nbqa-isort
        - id: nbqa-pyupgrade

See `.pre-commit-hooks.yaml <https://github.com/nbQA-dev/nbQA/blob/master/.pre-commit-hooks.yaml>`_ for all available built-in hooks.

Custom hooks
------------

If you have your own custom tool (e.g. ``customtool``) for which we currently don't have a built-in hook, you can define your own one with: ::

    - repo: https://github.com/nbQA-dev/nbQA
      rev: 0.3.6
      hooks:
        - id: nbqa
          args: [customtool]
          name: nbqa-customtool
          alias: nbqa-customtool
          additional_dependencies: [customtool]

If there are additional Python code quality tools you would like us to make a hook for, please :ref:`open a pull request<contributing>`
or let us know in the `issue tracker <https://github.com/nbQA-dev/nbQA/issues>`_!

Configuration
-------------

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
