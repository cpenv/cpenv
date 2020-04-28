# -*- coding: utf-8 -*-

# Third party imports
from nose.tools import assert_raises

# Local imports
import cpenv
from cpenv.utils import rmtree

# Local imports
from . import data_path


def setup_module():
    pass


def teardown_module():
    rmtree(data_path('home'))


def test_create():
    '''Create a module'''

    cpenv.create(data_path('home', 'testmod'), name='testmod', version='0')
    assert_raises(
        OSError,
        cpenv.create,
        data_path('home', 'testmod'),
        'testmod',
        '0'
    )
