# -*- coding: utf-8 -*-

# Standard library imports
import os
import sys


py_ver = sys.version_info[0]
is_py2 = py_ver == 2
is_py3 = py_ver == 3

if is_py2:
    string_types = (str, basestring, unicode)
    numeric_types = (int, long, float)

if is_py3:
    string_types = (str, bytes)
    numeric_types = (int, float)


platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin':  # Use osx instead of darwin
    platform = 'osx'
os.environ['CPENV_PLATFORM'] = platform
