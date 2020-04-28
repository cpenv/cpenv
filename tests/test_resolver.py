# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
from nose.tools import assert_raises, raises

# Local imports
from cpenv.resolver import ResolveError, Resolver
from cpenv.utils import parse_redirect, rmtree

# Local imports
from . import data_path
from .utils import cwd, make_files


ENV_TEXT = '''
environment:
    UNRESOLVED_PATH: $NOVAR
    RESOLVED_PATH: $MODULE/resolved
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

REDIRECT_TEXT = 'testmod testmodb testmodc'
REDIRECT_TEXT_END_NEWLINE = 'testmod testmodb testmodc\n'
REDIRECT_TEXT_MULTILINE = 'testmod\ntestmodb\ntestmodc\n'
REDIRECT_TEXT_MULTILINE2 = 'testmod\ntestmodb\ntestmodc\n \n     \n '
REDIRECT_TEXT_MULTILINE3 = 'testmod\ntestmodb\n\n \ntestmodc\n '


def setup_module():
    os.environ['CPENV_HOME'] = data_path('home')
    os.environ['CPENV_MODULES'] = data_path('modules')

    files = (
        data_path('home', 'modules', 'testmod', 'module.yml'),
        data_path('not_home', 'relmod', 'module.yml'),
        data_path('home', 'modules', 'testmodc', 'module.yml'),
        data_path('modules', 'testmod', 'module.yml'),
        data_path('modules', 'testmodb', 'module.yml'),
    )
    make_files(*files, text=ENV_TEXT)

    project_path = data_path('not_home', 'project', 'sequence', 'shot')
    os.makedirs(project_path)
    make_files(
        data_path('not_home', 'project', '.cpenv'),
        text=REDIRECT_TEXT
    )
    make_files(
        data_path('not_home', 'projecta', '.cpenv'),
        text=REDIRECT_TEXT_END_NEWLINE
    )
    make_files(
        data_path('not_home', 'projectb', '.cpenv'),
        text=REDIRECT_TEXT_MULTILINE
    )
    make_files(
        data_path('not_home', 'projectc', '.cpenv'),
        text=REDIRECT_TEXT_MULTILINE2
    )
    make_files(
        data_path('not_home', 'projectd', '.cpenv'),
        text=REDIRECT_TEXT_MULTILINE3
    )
    make_files(os.path.join(project_path, 'shot_file.txt'), text='')


def teardown_module():
    rmtree(data_path('home'))
    rmtree(data_path('not_home'))


def test_resolve_home():
    '''Resolve module in CPENV_HOME'''

    r = Resolver('testmod')
    r.resolve()
    assert r.resolved[0].path == data_path('home', 'modules', 'testmod')


def test_resolve_module_on_path():
    '''Resolve module in CPENV_MODULES path'''

    # Test resolve global module
    r = Resolver('testmodb')
    r.resolve()

    assert r.resolved[0].path == data_path('modules', 'testmodb')

    # Test resolve module in home, should take precedence over global
    # module of the same name
    r = Resolver('testmod')
    r.resolve()

    assert r.resolved[0].path == data_path('home', 'modules', 'testmod')

    # Test resoluve module in CPENV_HOME/modules
    r = Resolver('testmodc')
    r.resolve()

    assert r.resolved[0].path == data_path('home', 'modules', 'testmodc')

    # Test global module does not exist
    r = Resolver('testmod', 'does_not_exist')
    with assert_raises(ResolveError):
        r.resolve()


def test_resolve_relative():
    '''Resolve module from relative path'''

    with cwd(data_path('not_home')):
        r = Resolver('relmod')
        r.resolve()

    assert r.resolved[0].path == data_path('not_home', 'relmod')


def test_resolve_absolute():
    '''Resolve module from absolute path'''

    with cwd(data_path('not_home')):
        r = Resolver(data_path('home', 'modules', 'testmod'))
        r.resolve()

    assert r.resolved[0].path == data_path('home', 'modules', 'testmod')


def test_resolve_multi_args():
    '''Resolve multiple paths'''

    r = Resolver('testmod', 'testmodb', 'testmodc')
    r.resolve()
    assert len(r.resolved) == 3


def test_redirect_resolver_from_folder():
    '''Resolve module from folder, parent folder has .cpenv file'''

    expected_paths = [
        data_path('home', 'modules', 'testmod'),
        data_path('modules', 'testmodb'),
        data_path('home', 'modules', 'testmodc'),
    ]

    resolve_paths = [
        data_path('not_home', 'project', 'sequence', 'shot'),
        data_path('not_home', 'projecta'),
        data_path('not_home', 'projectb'),
        data_path('not_home', 'projectc'),
        data_path('not_home', 'projectd'),
    ]
    for path in resolve_paths:
        r = Resolver(path)
        r.resolve()

        assert r.resolved[0].path == expected_paths[0]
        assert r.resolved[1].path == expected_paths[1]
        assert r.resolved[2].path == expected_paths[2]


def test_redirect_resolver_from_file():
    '''Resolve module from file, parent folder has .cpenv file'''

    expected_paths = [
        data_path('home', 'modules', 'testmod'),
        data_path('modules', 'testmodb'),
        data_path('home', 'modules', 'testmodc'),
    ]

    r = Resolver(
        data_path('not_home', 'project', 'sequence', 'shot', 'shot_file.txt')
    )
    r.resolve()

    assert r.resolved[0].path == expected_paths[0]
    assert r.resolved[1].path == expected_paths[1]
    assert r.resolved[2].path == expected_paths[2]


@raises(ResolveError)
def test_nonexistant_virtualenv():
    '''Raise ResolveError when module does not exist'''

    r = Resolver('does_not_exist')
    r.resolve()


@raises(ResolveError)
def test_nonexistant_module():
    '''Raise ResolveError when module does not exist'''

    r = Resolver('testmod', 'does_not_exist')
    r.resolve()


@raises(ResolveError)
def test_multi_module_does_not_exist():
    '''Raise ResolveError when a module does not exist'''

    r = Resolver('testmod', 'testmodb', 'does_not_exist')
    r.resolve()


def test_parse_redirect():
    '''Test parse redirect strings.'''

    tests = [
        ('testenv testmod', ['testenv', 'testmod']),
        ('testenv testmod\n', ['testenv', 'testmod']),
        ('testenv\ntestmod\n', ['testenv', 'testmod']),
        ('testenv\ntestmod\ntestmodb', ['testenv', 'testmod', 'testmodb']),
        ('testenv testmod\n', ['testenv', 'testmod']),
        ('testenv\ntestmod\n', ['testenv', 'testmod']),
        ('testenv\ntestmod\n \n     \n ', ['testenv', 'testmod']),
        ('testenv\ntestm\n \ntestmod\n ', ['testenv', 'testm', 'testmod']),
    ]
    for test, expected in tests:
        assert parse_redirect(test) == expected
