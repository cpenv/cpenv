# -*- coding: utf-8 -*-

import sys

platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin': # Use osx instead of darwin
    platform = 'osx'

from .shell import *
from . import envutils
