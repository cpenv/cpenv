import os
import unittest
import shutil
import mock
import sys
from cpenv.resolver import Resolver
from cpenv.models import VirtualEnvironment, Module
from cpenv import platform
from nose.tools import raises
from . import data_path, make_files, cwd

ENVIRON = '''
# Environment variables in the environment section are expanded.
# Additionally the following variables are expanded:
#     $CPENV_ENVIRON - root of the virtual environment
#     $CPENV_MODULE - this modules root path
#     $CPENV_PLATFORM - system platform (win, osx, linux)
#     $CPENV_PYVER - the python version this environment uses


environment:
    UNRESOLVED_PATH: $NOVAR
    RESOLVED_PATH: $CPENV_ENVIRON/resolved
    PLATFORM_PATH:
        win: environ_win
        osx: environ_osx
        linux: environ_linux
    MULTI_PLATFORM_PATH:
        - nonplat
        - win:
            - $CPENV_PYVER/wina
            - $CPENV_PYVER/winb
          osx:
            - $CPENV_PYVER/osxa
            - $CPENV_PYVER/osxb
          linux:
            - $CPENV_PYVER/linuxa
            - $CPENV_PYVER/linuxb

'''

FILES = [
    data_path('home', 'test_environment', 'environment.yml'),
    data_path('home', 'test_environment', 'modules',
              'test_module', 'environment.yml'),
    data_path('not_home', 'test_environment', 'environment.yml'),
    data_path('cached', 'cached_environment', 'environment.yml')
]


def setup_module():

    make_files(data=ENVIRON, *FILES)
    os.environ['CPENV_HOME'] = data_path('home')


def teardown_module():

    shutil.rmtree(data_path('home'))
    shutil.rmtree(data_path('not_home'))
    shutil.rmtree(data_path('cached'))


class TestResolver(unittest.TestCase):
    '''Resolver Test Suite'''

    def test_resolve_home(self):
        '''Resolve environment in CPENV_HOME'''

        r = Resolver('test_environment')
        r.resolve()

        assert r.resolved[0].path == data_path('home', 'test_environment')

    def test_resolve_relative(self):
        '''Resolve environment from relative path'''

        with cwd(data_path('not_home')):
            r = Resolver('test_environment')
            r.resolve()

        assert r.resolved[0].path == data_path('not_home', 'test_environment')

    def test_resolve_absolute(self):
        '''Resolve environment from absolute path'''

        with cwd(data_path('not_home')):
            r = Resolver(data_path('home', 'test_environment'))
            r.resolve()

        assert r.resolved[0].path == data_path('home', 'test_environment')

    def test_resolve_cache(self):
        '''Resolve environment from cache'''

        cached_env_path = data_path('cached', 'cached_environment')
        mock_cache = mock.Mock()
        mock_cache.find = mock.Mock(
            return_value=VirtualEnvironment(cached_env_path)
        )

        r = Resolver('cached_environment', cache=mock_cache)
        r.resolve()

        assert r.resolved[0].path == cached_env_path

    def test_resolve_multi_args(self):
        '''Resolve multiple paths'''

        r = Resolver('test_environment', 'test_module')
        r.resolve()

        assert isinstance(r.resolved[0], VirtualEnvironment)
        assert isinstance(r.resolved[1], Module)

    def test_combine_multi_args(self):
        '''Resolve combine multiple paths'''

        pyver = str(sys.version[:3])
        expected = {
            'UNRESOLVED_PATH': '$NOVAR',
            'RESOLVED_PATH': data_path('home', 'test_environment', 'resolved'),
            'PLATFORM_PATH': 'environ_' + platform,
            'MULTI_PLATFORM_PATH': [
                'nonplat',
                pyver + '/' + platform + 'a',
                pyver + '/' + platform + 'b',
            ]
        }

        r = Resolver('test_environment', 'test_module')
        r.resolve()
        combined = r.combine()

        assert combined == expected

    @raises(NameError)
    def test_nonexistant_virtualenv(self):
        '''Raise NameError when environment does not exist'''

        r = Resolver('does_not_exist')
        r.resolve()

    @raises(NameError)
    def test_nonexistant_module(self):
        '''Raise NameError when module does not exist'''

        r = Resolver('test_environment', 'does_not_exist')
        r.resolve()

    @raises(NameError)
    def test_multi_module_does_not_exist(self):
        '''Raise NameError when a module does not exist'''

        r = Resolver('test_environment', 'test_module', 'does_not_exist')
        r.resolve()
