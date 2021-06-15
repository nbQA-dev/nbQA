==========
Pre-commit
==========

Usage
-----

You can easily use ``nbqa`` as a `pre-commit <https://pre-commit.com/>`_ hook.

Here's an example of what you could include in your ``.pre-commit-config.yaml`` file: ::

    repos:
    - repo: https://github.com/nbQA-dev/nbQA
      rev: 0.13.0
      hooks:
       - id: nbqa-black
         additional_dependencies: [black==20.8b1]
       - id: nbqa-pyupgrade
         additional_dependencies: [pyupgrade==2.7.3]
       - id: nbqa-isort
         additional_dependencies: [isort==5.6.4]

For best reproducibility, you should pin your dependencies (as above). Running ``pre-commit autoupdate`` will update your hooks' versions, but
versions of additional dependencies need to updated manually.

See `.pre-commit-hooks.yaml <https://github.com/nbQA-dev/nbQA/blob/master/.pre-commit-hooks.yaml>`_ for all available built-in hooks.

Custom hooks
------------

If you have your own custom tool (e.g. ``customtool``) for which we currently don't have a built-in hook, you can define your own one with: ::

    - repo: https://github.com/nbQA-dev/nbQA
      rev: 0.13.0
      hooks:
        - id: nbqa
          args: [customtool]
          name: nbqa-customtool
          alias: nbqa-customtool
          additional_dependencies: [customtool==<version number>]

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
