# -*- coding: utf-8 -*-

# Standard library imports
import os

# Local imports
import cpenv
from cpenv import paths


def data_path(*args):
    return paths.normalize(os.path.dirname(__file__), 'data', *args)


def setup_package():
    cpenv.set_home_path(data_path('home'))


def teardown_package():
    paths.rmtree(data_path())
