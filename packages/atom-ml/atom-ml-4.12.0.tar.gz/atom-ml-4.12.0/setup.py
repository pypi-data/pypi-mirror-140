# -*- coding: utf-8 -*-

"""
Automated Tool for Optimized Modelling (ATOM)
Author: Mavs
Description: Package's setup code.

"""

import setuptools


with open("README.md", encoding="utf8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf8") as f:
    requirements = f.read().splitlines()

with open("requirements-optional.txt", encoding="utf8") as f:
    optional_requirements = f.read().splitlines()

with open("requirements-test.txt", encoding="utf8") as f:
    test_requirements = f.read().splitlines()

setuptools.setup(
    name="atom-ml",
    version="4.12.0",
    license="MIT",
    description="A Python package for fast exploration of machine learning pipelines",
    download_url=f"https://github.com/tvdboom/ATOM/archive/v4.12.0.tar.gz",
    url="https://github.com/tvdboom/ATOM",
    author="tvdboom",
    author_email="m.524687@gmail.com",
    keywords=["Python package", "Machine Learning", "Modelling", "Data Pipeline"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["atom"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    extras_require={"models": optional_requirements},
    tests_require=test_requirements,
    python_requires=">=3.7"
)
