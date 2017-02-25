# -*- coding: utf-8 -*-

import os
import shutil
import unittest
from cpenv.hooks import HookFinder
from cpenv.models import VirtualEnvironment
from cpenv.utils import rmtree
from nose.tools import raises
from . import data_path
from .utils import make_files


HOOK_TEXT = '''
def run(env):
    return True
'''
MODULE_HOOK_TEXT = '''
def run(env, module):
    return True
'''


def setup_module():
    env_files = (
        data_path('home', 'testenv', 'environment.yml'),
        data_path('home', 'testenv', 'modules', 'testmod', 'module.yml'),
    )
    global_hook_files = (
        data_path('home', 'hooks', 'precreate.py'),
        data_path('home', 'hooks', 'postcreate.py'),
        data_path('home', 'hooks', 'preactivate.py'),
        data_path('home', 'hooks', 'postactivate.py'),
    )
    env_hook_files = (
        data_path('home', 'testenv', 'hooks', 'preactivate.py'),
        data_path('home', 'testenv', 'hooks', 'preactivatemodule.py'),
    )
    mod_hook_files = (
        data_path(
            'home', 'testenv', 'modules', 'testmod', 'hooks', 'postactivatemodule.py'
        ),
        data_path(
            'home', 'testenv', 'modules', 'testmod', 'hooks', 'postcreatemodule.py'
        ),
        data_path(
            'home', 'testenv', 'modules', 'testmod', 'hooks', 'precreatemodule.py'
        ),
    )
    make_files(text='', *env_files)
    make_files(text=HOOK_TEXT, *global_hook_files)
    make_files(text=HOOK_TEXT, *env_hook_files)
    make_files(text=MODULE_HOOK_TEXT, *mod_hook_files)


def teardown_module():
    rmtree(data_path('home'))


class TestHookFinder(unittest.TestCase):

    def setUp(self):

        self.hook_finder = HookFinder(
            data_path('home', 'testenv', 'modules', 'testmod', 'hooks'),
            data_path('home', 'testenv', 'hooks'),
            data_path('home', 'hooks'),
        )

    def test_hook_resolution(self):
        '''Test hook resolution'''

        hook = self.hook_finder('precreate')
        assert hook.__file__ == data_path('home', 'hooks', 'precreate.py')

        hook = self.hook_finder('preactivate')
        assert hook.__file__ == data_path('home', 'testenv',
                                          'hooks', 'preactivate.py')

        hook = self.hook_finder('postactivatemodule')
        assert hook.__file__ == data_path('home', 'testenv', 'modules',
                                          'testmod', 'hooks',
                                          'postactivatemodule.py')

    def test_env_hook(self):
        '''Test run environment hook'''

        env = VirtualEnvironment(data_path('home', 'testenv'))
        hook = self.hook_finder('precreate')
        assert hook.run(env) == True

    def test_mod_hook(self):
        '''Test run module hook'''

        env = VirtualEnvironment(data_path('home', 'testenv'))
        mod = env.get_module('testmod')
        hook = self.hook_finder('postactivatemodule')
        assert hook.run(env, mod) == True
        hook = self.hook_finder('postcreatemodule')
        assert hook.run(env, mod) == True
        hook = self.hook_finder('precreatemodule')
        assert hook.run(env, mod) == True

    def test_hook_not_found(self):
        '''Test hook not found'''

        hook = self.hook_finder('ppp')
        assert hook is None

    @raises(SyntaxError)
    def test_hook_syntaxerror(self):
        '''Test hook compile raises syntaxerror'''

        make_files(data_path('home', 'hooks', 'badhook.py'), text='x is = 4')
        self.hook_finder('badhook')

    @raises(IndexError)
    def test_hook_runerror(self):
        '''Test hook run raises error'''

        make_files(data_path('home', 'hooks', 'badrunhook.py'),
                   text='def run(env):\n\treturn env[1]')
        self.hook_finder('badrunhook').run([0])
