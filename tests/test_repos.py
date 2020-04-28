# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
from nose.tools import assert_raises, raises

# Local imports
import cpenv

# Local imports
from . import data_path


def setup_module():
    cpenv.create(
        where=data_path('modules', 'testmod-0.1.0'),
        name='testmod',
        version='0.1.0',
        description='A test module',
    )
    cpenv.create(
        where=data_path('modules', 'testmod-0.2.0'),
        name='testmod',
        version='0.2.0',
        description='A test module',
    )
    cpenv.create(
        where=data_path('modules', 'plugin-0.2.0'),
        name='plugin',
        version='0.2.0',
        description='A test module',
    )
    cpenv.create(
        where=data_path('modules', 'fresh/0.1.0'),
        name='fresh',
        version='0.1.0',
        description='A test module',
    )
    cpenv.create(
        where=data_path('modules', 'fresh/0.2.0'),
        name='fresh',
        version='0.2.0',
        description='A test module',
    )


def test_local_repo():
    ''''''

    local_repo = cpenv.LocalRepo(data_path('modules'))
    spec = local_repo.find_module('testmod-0.1.0')
