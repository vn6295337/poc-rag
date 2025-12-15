# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add source directory to path
sys.path.insert(0, os.path.abspath('../../src'))

# Project information
project = 'RAG Document Assistant'
copyright = '2025, AI Portfolio'
author = 'AI Portfolio'

# The full version, including alpha/beta/rc tags
release = '0.1.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

# Templates path
templates_path = ['_templates']

# Exclude patterns
exclude_patterns = []

# HTML theme
html_theme = 'sphinx_rtd_theme'

# Static files path
html_static_path = ['_static']

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}