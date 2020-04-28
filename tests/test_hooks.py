# -*- coding: utf-8 -*-

# Standard library imports
import unittest

# Third party imports
from nose.tools import raises

# Local imports
from cpenv.hooks import HookFinder
from cpenv.module import Module
from cpenv.utils import rmtree

# Local imports
from . import data_path
from .utils import make_files


HOOK_TEXT = '''
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
        data_path(
            'home', 'modules', 'testmod', 'hooks', 'postactivate.py'
        ),
        data_path(
            'home', 'modules', 'testmod', 'hooks', 'precreate.py'
        ),
        data_path(
            'home', 'modules', 'testmod', 'hooks', 'postcreate.py'
        ),
    )
    make_files(text='', *mod_files)
    make_files(text=HOOK_TEXT, *global_hook_files)
    make_files(text=MODULE_HOOK_TEXT, *mod_hook_files)


def teardown_module():
    rmtree(data_path('home'))


class TestHookFinder(unittest.TestCase):

    def setUp(self):

        self.hook_finder = HookFinder(
            data_path('home', 'modules', 'testmod', 'hooks'),
            data_path('home', 'hooks'),
        )

    def test_hook_resolution(self):
        '''Test hook resolution'''

        hook = self.hook_finder('preactivate')
        print(hook.__file__)
        print(data_path('home', 'hooks', 'preactivate.py'))
        assert hook.__file__ == data_path('home', 'hooks', 'preactivate.py')

        hook = self.hook_finder('postactivate')
        assert hook.__file__ == data_path('home', 'modules', 'testmod',
                                          'hooks', 'postactivate.py')

        hook = self.hook_finder('postcreate')
        assert hook.__file__ == data_path('home', 'modules', 'testmod',
                                          'hooks', 'postcreate.py')

        hook = self.hook_finder('precreate')
        assert hook.__file__ == data_path('home', 'modules', 'testmod',
                                          'hooks', 'precreate.py')

    def test_mod_hook(self):
        '''Test run module hook'''

        mod = Module(data_path('home', 'testmod'))
        hook = self.hook_finder('postactivate')
        assert hook.run(mod) is True
        hook = self.hook_finder('postcreate')
        assert hook.run(mod) is True
        hook = self.hook_finder('precreate')
        assert hook.run(mod) is True

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

        fake_module = []
        make_files(data_path('home', 'hooks', 'badrunhook.py'),
                   text='def run(module):\n\treturn module[1]')
        self.hook_finder('badrunhook').run(fake_module)
