#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral and QuatroPe.
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/uttrs/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""This file is for distribute uttrs

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import pathlib

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup  # noqa


# =============================================================================
# CONSTANTS
# =============================================================================

PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))

REQUIREMENTS = ["numpy", "attrs", "attrs", "astropy"]

with open(PATH / "README.md") as fp:
    LONG_DESCRIPTION = fp.read()

DESCRIPTION = (
    LONG_DESCRIPTION.splitlines()[2].replace("`", "'").replace("*", "'")
)


with open(PATH / "uttr.py") as fp:
    VERSION = (
        [line for line in fp.readlines() if line.startswith("__version__")][0]
        .split("=", 1)[-1]
        .strip()
        .replace('"', "")
    )

print(DESCRIPTION)


# =============================================================================
# FUNCTIONS
# =============================================================================

setup(
    name="uttrs",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="JB Cabral and QuatroPe",
    author_email="jbcabral@unc.edu.ar",
    url="https://github.com/quatrope/utts",
    license="3 Clause BSD",
    keywords=[
        "astronomy",
        "oop",
        "attrs",
        "units",
        "astropy",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
    ],
    py_modules=["uttr", "ez_setup"],
    install_requires=REQUIREMENTS,
)
