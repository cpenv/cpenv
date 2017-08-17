# -*- coding: utf-8 -*-

import os
from functools import partial
from cpenv.utils import rmtree

data_path = partial(os.path.join, os.path.dirname(__file__), 'data')


def setup_package():
    os.environ['CPENV_HOME'] = data_path('home')


def teardown_package():
    rmtree(data_path())
