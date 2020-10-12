========================
Usage as pre-commit hook
========================

You can easily use `nbqa` as a `pre-commit <https://pre-commit.com/>`_ hook by passing your desired
code quality tool in the ``args`` and ``additional_dependencies`` sections.

For example, if you wanted to autoformat your notebooks using ``black``, check for style guide compliance with ``flake8``,
and sort your imports using ``isort``, you could put the following in your ``.pre-commit-config.yaml`` file ::

    repos:
    - repo: 'https://github.com/nbQA-dev/nbQA'
        rev: 0.3.0
        hooks:
        - id: nbqa
            args:
            - black
            name: nbqa-black
            alias: nbqa-black
            additional_dependencies:
            - black
        - id: nbqa
            args:
            - flake8
            name: nbqa-flake8
            alias: nbqa-flake8
            additional_dependencies:
            - flake8
        - id: nbqa
            args:
            - isort
            name: nbqa-isort
            alias: nbqa-isort
            additional_dependencies:
            - isort

See :ref:`configuration<configuration>` for how to further configure ``nbqa``.
