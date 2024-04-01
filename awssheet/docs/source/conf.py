# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


# import os
# import sys
# sys.path.insert(0, os.path.abspath('..'))
# # os.environ['DJANGO_SETTINGS_MODULE'] = 'awssheet.settings'
# import django
# django.setup()
import sphinx_rtd_theme
project = 'iAWS'
copyright = '2024, Infrastructure As Worksheet'
author = 'Damanjeet Singh'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration



# Set the theme to Read the Docs
html_theme = 'sphinx_rtd_theme'
templates_path = ['_templates']
extensions = [
    'sphinx.ext.autodoc',  # Include documentation from docstrings
    'sphinx.ext.viewcode',  # Add links to source code
    'sphinx.ext.todo',      # Support for todo items
    'sphinx_rtd_theme',     # Use the Read The Docs theme
]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'

html_static_path = ['_static']

# Add custom CSS file
html_css_files = [
    'css/custom_theme.css',
]
