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
    assert result['var'] == ['0', '1', 'x', 'y', 'z']


def test_join_case_insensitivity():
    '''join_dicts - is case insensitive.'''

    a = {'Var': 'a'}  # Original mixed case
    b = {'VAR': 'b'}  # UPPER - set
    c = {'var': ['0', '1']}  # lower - prepend

    # Ensure Var is properly set and case of key is changed
    result = mappings.join_dicts(a, b)
    assert result['VAR'] == 'b'

    # Ensure Var is properly set, prepended to and case of key is changed
    result = mappings.join_dicts(a, b, c)
    assert result['var'] == ['0', '1', 'b']


def test_env_to_dict():
    '''env_to_dict - convert environment mapping to dict'''

    env = {
        'PATH': 'X:Y:Z',
        'VAR': 'VALUE',
    }
    result = mappings.env_to_dict(env, pathsep=':')
    assert result == {'PATH': ['X', 'Y', 'Z'], 'VAR': 'VALUE'}


def test_dict_to_env():
    '''dict_to_env - convert dict to environment mapping'''

    data = {
        'PATH': ['X', 'Y', 'Z'],
        'VAR': 'VALUE',
    }
    result = mappings.dict_to_env(data, pathsep=':')
    assert result == {'PATH': 'X:Y:Z', 'VAR': 'VALUE'}
