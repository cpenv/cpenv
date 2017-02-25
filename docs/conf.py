# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(1, os.path.abspath('..'))

# Mock stuff
from mock import Mock as MagicMock
class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()
MOCK_MODULES = ['virtualenv',]
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

import cpenv
import sphinx_rtd_theme

project = cpenv.__title__
copyright = '2015-2017, ' + cpenv.__author__
author = cpenv.__author__
version = cpenv.__version__
release = cpenv.__version__

source_suffix = '.rst'
master_doc = 'index'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode'
]
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'collapse_navigation': False,
    'display_version': False,
}
html_static_path = ['static']
htmlhelp_basename = 'cpenvdoc'
latex_elements = {}
latex_documents = []
man_pages = [
    (master_doc, 'cpenv', u'cpenv Documentation',
     [author], 1)
]
texinfo_documents = []
intersphinx_mapping = {'https://docs.python.org/': None}
