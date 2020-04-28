# -*- coding: utf-8 -*-
'''isort:skip_file'''
__title__ = 'cpenv'
__version__ = '0.5.0'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__url__ = 'http://github.com/cpenv/cpenv'
__license__ = 'MIT'
__description__ = 'Cross-platform Python environment management.'


# Standard library imports
import os
import sys


platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin':  # Use osx instead of darwin
    platform = 'osx'
os.environ['CPENV_PLATFORM'] = platform


# Local imports
from . import deps, versions
from .api import *
from .repos import *
from .resolver import *
