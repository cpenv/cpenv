# -*- coding: utf-8 -*-

# Standard library imports
import unittest

# Third party imports
import pytest

# Local imports
from cpenv import paths
from cpenv.hooks import HookFinder
from cpenv.module import Module

from . import data_path
from .utils import make_files

GLOBAL_HOOK_TEXT = '''
def run(module):
    return True
'''
MODULE_HOOK_TEXT = '''
def run(module):
    return True
'''


def setup_module():
    mod_files = (
        data_path('home', 'modules', 'testmod', 'module.yml'),
    )
    global_hook_files = (
        data_path('home', 'hooks', 'precreate.py'),
        data_path('home', 'hooks', 'postcreate.py'),
        data_path('home', 'hooks', 'preactivate.py'),
        data_path('home', 'hooks', 'postactivate.py'),
    )
    mod_hook_files = (
        data_path('home', 'modules', 'testmod', 'hooks', 'postactivate.py'),
        data_path('home', 'modules', 'testmod', 'hooks', 'precreate.py'),
        data_path('home', 'modules', 'testmod', 'hooks', 'postcreate.py'),
    )
    make_files(text='', *mod_files)
    make_files(text=GLOBAL_HOOK_TEXT, *global_hook_files)
    make_files(text=MODULE_HOOK_TEXT, *mod_hook_files)


def teardown_module():
    paths.rmtree(data_path('home'))


@pytest.fixture
def hook_finder():
    return HookFinder(
        data_path('home', 'modules', 'testmod', 'hooks'),
        data_path('home', 'hooks'),
    )


def test_hook_resolution(hook_finder):
    '''HookFinder resolve in correct order'''

    hook = hook_finder('preactivate')
    assert hook.__file__ == data_path('home', 'hooks', 'preactivate.py')

    hook = hook_finder('postactivate')
    assert hook.__file__ == data_path('home', 'modules', 'testmod',
                                      'hooks', 'postactivate.py')

    hook = hook_finder('postcreate')
    assert hook.__file__ == data_path('home', 'modules', 'testmod',
                                      'hooks', 'postcreate.py')

    hook = hook_finder('precreate')
    assert hook.__file__ == data_path('home', 'modules', 'testmod',
                                      'hooks', 'precreate.py')

def test_mod_hook(hook_finder):
    '''Run module-level hooks'''

    mod = Module(data_path('home', 'testmod'))
    assert mod.run_hook('precreate')
    assert mod.run_hook('postcreate')
    assert mod.run_hook('postactivate')

def test_hook_not_found(hook_finder):
    '''HookFinder returns None for missing hook'''

    hook = hook_finder('ppp')
    assert hook is None

def test_hook_syntaxerror(hook_finder):
    '''HookFinder raises SytanxError'''

    make_files(data_path('home', 'hooks', 'badhook.py'), text='x is = 4')

    with pytest.raises(SyntaxError):
        hook_finder('badhook')

def test_hook_runerror(hook_finder):
    '''Hook.run exceptions bubble up.'''

    fake_module = []
    make_files(data_path('home', 'hooks', 'badrunhook.py'),
               text='def run(module):\n\treturn module[1]')

    with pytest.raises(IndexError):
        hook_finder('badrunhook').run(fake_module)
