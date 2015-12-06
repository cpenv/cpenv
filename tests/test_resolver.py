import os
import shutil
import mock
import sys
from cpenv.resolver import Resolver
from cpenv.models import VirtualEnvironment, Module
from cpenv import platform
from nose.tools import raises
from . import data_path, make_files, cwd

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


def setup_module():
    files = (
        data_path('home', 'testenv', 'environment.yml'),
        data_path('home', 'testenv', 'modules', 'testmod', 'module.yml'),
        data_path('not_home', 'testenv', 'environment.yml'),
        data_path('cached', 'cachedenv', 'environment.yml')
    )
    make_files(text=ENV_TEXT, *files)
    os.environ['CPENV_HOME'] = data_path('home')


def teardown_module():
    shutil.rmtree(data_path('home'))
    shutil.rmtree(data_path('not_home'))
    shutil.rmtree(data_path('cached'))


def test_resolve_home():
    '''Resolve environment in CPENV_HOME'''

    r = Resolver('testenv')
    r.resolve()

    assert r.resolved[0].path == data_path('home', 'testenv')


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
        'PATH': [data_path('home', 'testenv', 'bin')],
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
        assert expected[k] == combined[k]


@raises(NameError)
def test_nonexistant_virtualenv():
    '''Raise NameError when environment does not exist'''

    r = Resolver('does_not_exist')
    r.resolve()


@raises(NameError)
def test_nonexistant_module():
    '''Raise NameError when module does not exist'''

    r = Resolver('testenv', 'does_not_exist')
    r.resolve()


@raises(NameError)
def test_multi_module_does_not_exist():
    '''Raise NameError when a module does not exist'''

    r = Resolver('testenv', 'testmod', 'does_not_exist')
    r.resolve()
