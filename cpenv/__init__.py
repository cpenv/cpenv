# -*- coding: utf-8 -*-

__title__ = 'cpenv'
__version__ = '0.3.5'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__url__ = 'http://github.com/cpenv/cpenv'
__license__ = 'MIT'
__description__ = 'Cross-platform Python environment management.'


import sys
import os

platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin':  # Use osx instead of darwin
    platform = 'osx'
os.environ['CPENV_PLATFORM'] = platform

from . import log
from .api import *
