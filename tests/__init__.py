# -*- coding: utf-8 -*-

# Standard library imports
import os

# Local imports
import cpenv
from cpenv import paths


def data_path(*args):
    return paths.normalize(os.path.dirname(__file__), 'data', *args)
