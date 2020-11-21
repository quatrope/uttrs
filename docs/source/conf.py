# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import pathlib


# this path is pointing to project/docs/source
CURRENT_PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
UTTRS_PATH = CURRENT_PATH.parent.parent

sys.path.insert(0, str(UTTRS_PATH))

import uttr


# -- Project information -----------------------------------------------------

project = 'uttrs'
copyright = '2020, QuatroPe'
author = 'JBCabral and QuatroPe'

# The full version, including alpha/beta/rc tags
release = uttr.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'nbsphinx']

exclude_patterns = ['_build', 'source/.ipynb_checkpoints/*']

numpydoc_class_members_toctree = False

nbsphinx_execute = 'never'  # access the server is slow



# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'bootstrap-astropy'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}

# =============================================================================
# PREPROCESS RST
# =============================================================================

html_logo = "_static/logo.png"

html_css_files = [
    'custom.css',
]

html_theme_options = {
    'logotext1': 'Uttrs',  # white,  semi-bold
    'logotext2': '',  # orange, light
    'logotext3': ':docs',   # white,  light
    'astropy_project_menubar': False
    }


import m2r

with open(UTTRS_PATH / "README.md") as fp:
    md = fp.read()


index = f"""
..
   Automatic created file. Don't edit


{m2r.convert(md)}

Contents:
---------

.. toctree::
    :maxdepth: 3

    tutorial.ipynb
    api.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

"""

with open(CURRENT_PATH / "index.rst", "w") as fp:
    fp.write(index)
