# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

from flopy.utils.get_modflow import run_main as get_modflow

sys.path.insert(0, os.path.abspath("../"))
from modflowapi import __version__

# -- Determine if this is a development or release version ------------------
branch_or_version = __version__ if "dev" not in __version__ else "develop"

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "modflowapi"
copyright = "2025, modflowapi developers"
author = "modflowapi developers"
release = "0.3.0.dev0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary", "myst_parser", "nbsphinx"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/Extensions.py"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- nbsphinx configuration -------------------------------------------------
nbsphinx_custom_formats = {
    ".py": ["jupytext.reads", {"fmt": "py:light"}],
}

# -- Install MODFLOW --------------------------------------------------------
bindir = Path.cwd() / "examples" / "notebooks"
repo = "modflow6-nightly-build" if branch_or_version == "develop" else "modflow6"
get_modflow(str(bindir), repo=repo)
