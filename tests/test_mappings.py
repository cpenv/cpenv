# -*- coding: utf-8 -*-

# Standard library imports
import os

# Local imports
from cpenv import mappings
from cpenv.compat import platform


_env = os.environ.copy()


def test_preprocessor():
    '''preprocess_dict - expand platform variables.'''

    plat_value = {'win': 'win', 'osx': 'osx', 'linux': 'linux'}
    data = {
        'strvar': plat_value,
        'listvar': [plat_value, 'b', 'c'],
    }
    result = mappings.preprocess_dict(data)
    assert result['strvar'] == platform
    assert result['listvar'] == [platform, 'b', 'c']


def test_set_values():
    '''join_dicts - set values.'''

    a = {'var': ['x', 'y']}
    b = {'var': 'z'}
    c = {'var': 'a'}

    result = mappings.join_dicts(a, b)
    assert result['var'] == b['var']

    result = mappings.join_dicts(a, b, c)
    assert result['var'] == c['var']


def test_prepend_values():
    '''join_dicts - prepend values.'''

    a = {'var': 'z'}
    b = {'var': ['x', 'y']}
    c = {'var': ['0', '1']}

    result = mappings.join_dicts(a, b)
    assert result['var'] == ['x', 'y', 'z']

    result = mappings.join_dicts(a, b, c)
    print(result)
    assert result['var'] == ['0', '1', 'x', 'y', 'z']
