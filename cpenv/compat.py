# -*- coding: utf-8 -*-

import sys

version = sys.version_info[0]
is_py2 = version == 2
is_py3 = version == 3

if is_py2:
    string_types = (str, basestring, unicode)
    numeric_types = (int, long, float)

if is_py3:
    string_types = (str, bytes)
    numeric_types = (int, float)
