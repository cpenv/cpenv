import os
import unittest
import shutil
import mock
from cpenv.resolver import Resolver
from cpenv.api import VirtualEnvironment
from nose.tools import raises
from . import data_path, make_files, cwd


FILES = [
    data_path('home', 'test_environment', 'environment.yml'),
    data_path('not_home', 'test_environment', 'environment.yml'),
    data_path('cached', 'cached_environment', 'environment.yml')
]


def setup_module():

    make_files(*FILES)
    os.environ['CPENV_HOME'] = data_path('home')


def teardown_module():

    shutil.rmtree(data_path('home'))
    shutil.rmtree(data_path('not_home'))
    shutil.rmtree(data_path('cached'))


class TestResolver(unittest.TestCase):

    def test_resolve_home(self):
        '''Resolve environment in CPENV_HOME'''

        resolver = Resolver('test_environment')
        env_path = resolver.resolve()

        self.assertEquals(env_path, data_path('home', 'test_environment'))

    def test_resolve_relative(self):
        '''Resolve environment from relative path'''

        with cwd(data_path('not_home')):
            resolver = Resolver('test_environment')
            env_path = resolver.resolve()

        self.assertEquals(env_path, data_path('not_home', 'test_environment'))

    def test_resolve_absolute(self):
        '''Resolve environment from absolute path'''

        with cwd(data_path('not_home')):
            resolver = Resolver(data_path('home', 'test_environment'))
            env_path = resolver.resolve()

        self.assertEquals(env_path, data_path('home', 'test_environment'))

    def test_resolve_cache(self):
        '''Resolve environment from cache'''

        cached_env_path = data_path('cached', 'cached_environment')
        mock_cache = mock.Mock()
        mock_cache.find = mock.Mock(
            return_value=VirtualEnvironment(cached_env_path)
        )

        resolver = Resolver('cached_environment', cache=mock_cache)
        env_path = resolver.resolve()

        self.assertEquals(env_path, cached_env_path)

    @raises(NameError)
    def test_resolve_nonexistant(self):
        '''Raise NameError when environment does not exist'''

        resolver = Resolver('nonexistant_environment')
        resolver.resolve()
