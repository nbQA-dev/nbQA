#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst", encoding="utf8") as readme_file:
    readme = readme_file.read()
    readme = readme.replace(
        '.. raw:: html\n\n    <p align="center">\n        <a href="#readme">\n            <img alt="demo" src="https://raw.githubusercontent.com/nbQA-dev/nbQA-demo/master/demo.gif">\n        </a>\n    </p>\n\n',  # noqa
        "",
    )

requirements = []

setup_requirements = []

test_requirements = []

setup(
    author="Marco Gorelli",
    author_email="m.e.gorelli@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Run any Python code quality tool on a Jupyter Notebook!",
    entry_points={"console_scripts": ["nbqa=nbqa.__main__:main"]},
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="nbqa",
    name="nbqa",
    packages=find_packages(include=["nbqa", "nbqa.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/MarcoGorelli/nbQA",
    version="0.1.20",
    zip_safe=False,
)
