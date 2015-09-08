# -*- coding: utf-8 -*-

import sys
import os

platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin': # Use osx instead of darwin
    platform = 'osx'
os.environ['CPENV_PLATFORM'] = platform

from . import log, vendor
from .api import *
from . import envutils, utils, shell
