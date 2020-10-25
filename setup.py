#!/usr/bin/env python

"""The setup script."""
from pathlib import Path

from setuptools import find_packages, setup

readme = Path("README.md").read_text(encoding="utf8")

requirements = ["toml"]

setup_requirements = []

test_requirements = []

extra_requirements = {
    "toolchain": ["black", "mypy", "isort", "pyupgrade", "flake8", "pylint"]
}

setup(
    author="Marco Gorelli, Girish Pasupathy",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Run any Python code quality tool on a Jupyter Notebook!",
    entry_points={"console_scripts": ["nbqa=nbqa.__main__:main"]},
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="nbqa",
    name="nbqa",
    packages=find_packages(include=["nbqa", "nbqa.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    url="https://github.com/nbQA-dev/nbQA",
    version="0.3.5",
    zip_safe=False,
)
