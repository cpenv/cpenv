# -*- coding: utf-8 -*-

import os
import mock
import sys
from cpenv.resolver import Resolver, ResolveError
from cpenv.models import VirtualEnvironment, Module
from cpenv import platform
from cpenv.utils import rmtree
from . import data_path
from .utils import make_files, cwd
from nose.tools import raises, assert_raises


ENV_TEXT = '''
environment:
    UNRESOLVED_PATH: $NOVAR
    RESOLVED_PATH: $ENVIRON/resolved
    PLATFORM_PATH:
        win: environ_win
        osx: environ_osx
        linux: environ_linux
    MULTI_PLATFORM_PATH:
        - nonplat
        - win:
            - $PYVER/wina
            - $PYVER/winb
          osx:
            - $PYVER/osxa
            - $PYVER/osxb
          linux:
            - $PYVER/linuxa
            - $PYVER/linuxb
'''

REDIRECT_TEXT = '''testenv testmod'''


def setup_module():
    os.environ['CPENV_HOME'] = data_path('home')
    os.environ['CPENV_MODULES'] = data_path('modules')

    files = (
        data_path('home', 'testenv', 'environment.yml'),
        data_path('home', 'testenv', 'modules', 'testmod', 'module.yml'),
        data_path('not_home', 'testenv', 'environment.yml'),
        data_path('cached', 'cachedenv', 'environment.yml'),
        data_path('modules', 'testmod', 'module.yml'),
        data_path('modules', 'testmodb', 'module.yml'),
        data_path('home', 'modules', 'testmodc', 'module.yml'),
    )
    make_files(*files, text=ENV_TEXT)

    project_path = data_path('not_home', 'project', 'sequence', 'shot')
    os.makedirs(project_path)
    make_files(data_path('not_home', 'project', '.cpenv'), text=REDIRECT_TEXT)
    make_files(os.path.join(project_path, 'shot_file.txt'), text='')


def teardown_module():
    rmtree(data_path('home'))
    rmtree(data_path('not_home'))
    rmtree(data_path('cached'))


def test_resolve_home():
    '''Resolve environment in CPENV_HOME'''

    r = Resolver('testenv')
    r.resolve()

    assert r.resolved[0].path == data_path('home', 'testenv')


def test_resolve_module_on_path():
    '''Resolve module in CPENV_MODULES path'''

    # Test resolve global module
    r = Resolver('testmod')
    r.resolve()

    assert r.resolved[0].path == data_path('modules', 'testmod')

    # Test resolve module in environment, should take precedence over global
    # module of the same name
    r = Resolver('testenv', 'testmod')
    r.resolve()

    assert r.resolved[1].path == data_path('home', 'testenv', 'modules', 'testmod')

    # Test resolve environment with global module
    r = Resolver('testenv', 'testmodb')
    r.resolve()

    assert r.resolved[1].path == data_path('modules', 'testmodb')

    # Test resoluve module in CPENV_HOME/modules
    r = Resolver('testmodc')
    r.resolve()

    assert r.resolved[0].path == data_path('home', 'modules', 'testmodc')

    # Test global module does not exist
    r = Resolver('testenv', 'does_not_exist')
    with assert_raises(ResolveError):
        r.resolve()


def test_resolve_relative():
    '''Resolve environment from relative path'''

    with cwd(data_path('not_home')):
        r = Resolver('testenv')
        r.resolve()

    assert r.resolved[0].path == data_path('not_home', 'testenv')


def test_resolve_absolute():
    '''Resolve environment from absolute path'''

    with cwd(data_path('not_home')):
        r = Resolver(data_path('home', 'testenv'))
        r.resolve()

    assert r.resolved[0].path == data_path('home', 'testenv')


def test_resolve_cache():
    '''Resolve environment from cache'''

    cached_env_path = data_path('cached', 'cachedenv')
    mock_cache = mock.Mock()
    mock_cache.find = mock.Mock(
        return_value=VirtualEnvironment(cached_env_path)
    )

    r = Resolver('cachedenv', cache=mock_cache)
    r.resolve()

    assert r.resolved[0].path == cached_env_path


def test_resolve_multi_args():
    '''Resolve multiple paths'''

    r = Resolver('testenv', 'testmod')
    r.resolve()

    assert isinstance(r.resolved[0], VirtualEnvironment)
    assert isinstance(r.resolved[1], Module)


def test_combine_multi_args():
    '''Resolve combine multiple paths'''

    pyver = str(sys.version[:3])
    expected = {
        'PATH': [{
            'win': data_path('home', 'testenv', 'Scripts'),
            'linux': data_path('home', 'testenv', 'bin'),
            'osx': data_path('home', 'testenv', 'bin')
        }[platform]],
        'CPENV_ACTIVE_MODULES': [],
        'UNRESOLVED_PATH': '$NOVAR',
        'RESOLVED_PATH': data_path('home', 'testenv', 'resolved'),
        'PLATFORM_PATH': 'environ_' + platform,
        'MULTI_PLATFORM_PATH': [
            'nonplat',
            pyver + '/' + platform + 'a',
            pyver + '/' + platform + 'b',
        ]
    }

    r = Resolver('testenv', 'testmod')
    r.resolve()
    combined = r.combine()

    for k in expected.keys():
        if isinstance(expected[k], list):
            assert expected[k] == combined[k]
            continue
        assert os.path.normpath(expected[k]) == os.path.normpath(combined[k])


def test_redirect_resolver_from_folder():
    '''Resolve environment from folder, parent folder has .cpenv file'''

    expected_paths = [
        data_path('home', 'testenv'),
        data_path('home', 'testenv', 'modules', 'testmod'),
    ]

    r = Resolver(data_path('not_home', 'project', 'sequence', 'shot'))
    r.resolve()

    assert r.resolved[0].path == expected_paths[0]
    assert r.resolved[1].path == expected_paths[1]


def test_redirect_resolver_from_file():
    '''Resolve environment from file, parent folder has .cpenv file'''

    expected_paths = [
        data_path('home', 'testenv'),
        data_path('home', 'testenv', 'modules', 'testmod'),
    ]

    r = Resolver(
        data_path('not_home', 'project', 'sequence', 'shot', 'shot_file.txt')
    )
    r.resolve()

    assert r.resolved[0].path == expected_paths[0]
    assert r.resolved[1].path == expected_paths[1]


@raises(ResolveError)
def test_nonexistant_virtualenv():
    '''Raise ResolveError when environment does not exist'''

    r = Resolver('does_not_exist')
    r.resolve()


@raises(ResolveError)
def test_nonexistant_module():
    '''Raise ResolveError when module does not exist'''

    r = Resolver('testenv', 'does_not_exist')
    r.resolve()


@raises(ResolveError)
def test_multi_module_does_not_exist():
    '''Raise ResolveError when a module does not exist'''

    r = Resolver('testenv', 'testmod', 'does_not_exist')
    r.resolve()
