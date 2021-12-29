import os
import re
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))
import sphinx

# Include todo list
todo_include_todos = True

# -- Project information -----------------------------------------------------

project = 'Math-Magik'
copyright = '2021, Roie R. Black'
author = 'Roie R. Black'
version = '0.1.0'

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx_ext.wordcount',
    'sphinx_ext.scad',
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.spelling',
    'sphinxcontrib.programoutput',
    'sphinx.ext.imgmath',
]

imgmath_font_size = 16

from os.path import dirname
a4_base_path = dirname(__file__) + 'grammars'

linkckeck_timeout = 3
linkcheck_retries = 2
spelling_word_list_filename = ['spelling_wordlist.txt']

master_doc = 'contents'
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

project = 'Math Magik'
copyright = '2021, Roie R. Black'
release = version
show_authors = True

rst_prolog = """
..  include::   /header.inc
"""

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx13'
html_theme_path = ['_themes']
html_static_path = ['_static']
html_sidebars = {'index': ['indexsidebar.html', 'searchbox.html']}
html_additional_pages = {'index': 'index.html'}
html_logo = '_static/badge.svg'

# -- Options for LaTeX output --------------------------------------------------

latex_documents = [('contents', 'magik.tex', 'Math Magik Projects',
                    'Roie R. Black', 'manual', 1)]
latex_logo = '_static/pylit.png'

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '11pt',
    'fontenc': r'\usepackage[LGR,X2,T1]{fontenc}',
}
