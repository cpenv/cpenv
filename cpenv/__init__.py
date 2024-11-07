# -*- coding: utf-8 -*-
"""isort:skip_file"""
__title__ = "cpenv"
__version__ = "0.5.37"
__author__ = "Dan Bradham"
__email__ = "danielbradham@gmail.com"
__url__ = "http://github.com/cpenv/cpenv"
__license__ = "MIT"
__description__ = "Cross-platform Python environment management."


# Local imports
from .api import *
from .module import *
from .repos import *
from .reporter import *
from .resolver import *
from .versions import *
from . import vendor
from . import paths
from . import compat
from . import mappings


# Initialize cpenv
from .api import _init

_init()
