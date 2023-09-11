# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
import pytest

# Local imports
import cpenv
from cpenv import paths

from . import data_path
from .utils import cwd, make_files

ENV_TEXT = """
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
"""

REDIRECT_TEXT = "testmod testmodb testmodc"
REDIRECT_TEXT_END_NEWLINE = "testmod testmodb testmodc\n"
REDIRECT_TEXT_MULTILINE = "testmod\ntestmodb\ntestmodc\n"
REDIRECT_TEXT_MULTILINE2 = "testmod\ntestmodb\ntestmodc\n \n     \n "
REDIRECT_TEXT_MULTILINE3 = "testmod\ntestmodb\n\n \ntestmodc\n "


def setup_module():
    cpenv.set_home_path(data_path("home"))
    cpenv.add_module_path(data_path("modules"))

    files = (
        data_path("home", "modules", "testmod", "module.yml"),
        data_path("not_home", "relmod", "module.yml"),
        data_path("home", "modules", "testmodc", "module.yml"),
        data_path("modules", "testmod", "module.yml"),
        data_path("modules", "testmodb", "module.yml"),
    )
    make_files(*files, text=ENV_TEXT)

    project_path = data_path("not_home", "project", "sequence", "shot")
    os.makedirs(project_path)
    make_files(data_path("not_home", "project", ".cpenv"), text=REDIRECT_TEXT)
    make_files(
        data_path("not_home", "projecta", ".cpenv"), text=REDIRECT_TEXT_END_NEWLINE
    )
    make_files(
        data_path("not_home", "projectb", ".cpenv"), text=REDIRECT_TEXT_MULTILINE
    )
    make_files(
        data_path("not_home", "projectc", ".cpenv"), text=REDIRECT_TEXT_MULTILINE2
    )
    make_files(
        data_path("not_home", "projectd", ".cpenv"), text=REDIRECT_TEXT_MULTILINE3
    )
    make_files(os.path.join(project_path, "shot_file.txt"), text="")


def teardown_module():
    paths.rmtree(data_path("modules"))
    paths.rmtree(data_path("home"))
    paths.rmtree(data_path("not_home"))


def test_resolve_home():
    """Resolve module in CPENV_HOME"""

    r = cpenv.Resolver(cpenv.get_repos())
    resolved = r.resolve(["testmod"])
    assert resolved[0].path == data_path("home", "modules", "testmod")


def test_resolve_module_on_path():
    """Resolve module in CPENV_MODULES path"""

    r = cpenv.Resolver(cpenv.get_repos())

    # Test resolve global module
    resolved = r.resolve(["testmodb"])
    assert resolved[0].path == data_path("modules", "testmodb")

    # Test resolve module in home, should take precedence over global
    # module of the same name
    resolved = r.resolve(["testmod"])
    assert resolved[0].path == data_path("home", "modules", "testmod")

    # Test resoluve module in CPENV_HOME/modules
    resolved = r.resolve(["testmodc"])
    assert resolved[0].path == data_path("home", "modules", "testmodc")

    # Test global module does not exist
    with pytest.raises(cpenv.ResolveError):
        r.resolve(["testmod", "does_not_exist"])


def test_resolve_relative():
    """Resolve module from relative path"""

    with cwd(data_path("not_home")):
        r = cpenv.Resolver(cpenv.get_repos())
        resolved = r.resolve(["relmod"])

    assert resolved[0].path == data_path("not_home", "relmod")


def test_resolve_multi_args():
    """Resolve multiple paths"""

    r = cpenv.Resolver(cpenv.get_repos())

    resolved = r.resolve(["testmod", "testmodb", "testmodc"])
    assert len(resolved) == 3


def test_redirect_resolver_from_folder():
    """Resolve module from folder, parent folder has .cpenv file"""

    expected_paths = [
        data_path("home", "modules", "testmod"),
        data_path("modules", "testmodb"),
        data_path("home", "modules", "testmodc"),
    ]

    resolve_paths = [
        data_path("not_home", "project", "sequence", "shot"),
        data_path("not_home", "projecta"),
        data_path("not_home", "projectb"),
        data_path("not_home", "projectc"),
        data_path("not_home", "projectd"),
    ]
    r = cpenv.Resolver(cpenv.get_repos())
    for path in resolve_paths:
        resolved = r.resolve([path])

        assert resolved[0].path == expected_paths[0]
        assert resolved[1].path == expected_paths[1]
        assert resolved[2].path == expected_paths[2]


def test_redirect_resolver_from_file():
    """Resolve module from file, parent folder has .cpenv file"""

    expected_paths = [
        data_path("home", "modules", "testmod"),
        data_path("modules", "testmodb"),
        data_path("home", "modules", "testmodc"),
    ]

    r = cpenv.Resolver(cpenv.get_repos())
    resolved = r.resolve(
        [data_path("not_home", "project", "sequence", "shot", "shot_file.txt")]
    )

    assert resolved[0].path == expected_paths[0]
    assert resolved[1].path == expected_paths[1]
    assert resolved[2].path == expected_paths[2]


def test_nonexistant_module():
    """Raise cpenv.ResolveError when module does not exist"""

    with pytest.raises(cpenv.ResolveError):
        r = cpenv.Resolver(cpenv.get_repos())
        r.resolve(["testmod", "does_not_exist"])


def test_multi_module_does_not_exist():
    """Raise cpenv.ResolveError when a module does not exist"""

    with pytest.raises(cpenv.ResolveError):
        r = cpenv.Resolver(cpenv.get_repos())
        r.resolve(["testmod", "testmodb", "does_not_exist"])


def test_parse_redirect():
    """Parse various redirect strings"""

    tests = [
        ("testenv testmod", ["testenv", "testmod"]),
        ("testenv testmod\n", ["testenv", "testmod"]),
        ("testenv\ntestmod\n", ["testenv", "testmod"]),
        ("testenv\ntestmod\ntestmodb", ["testenv", "testmod", "testmodb"]),
        ("testenv testmod\n", ["testenv", "testmod"]),
        ("testenv\ntestmod\n", ["testenv", "testmod"]),
        ("testenv\ntestmod\n \n     \n ", ["testenv", "testmod"]),
        ("testenv\ntestm\n \ntestmod\n ", ["testenv", "testm", "testmod"]),
    ]
    for test, expected in tests:
        assert cpenv.parse_redirect(test) == expected


def test_ignore_unresolved():
    """Test ignore_unresolved parameter."""

    r = cpenv.Resolver(cpenv.get_repos())

    resolved = r.resolve(
        ["testmod", "DOESNOTEXISTA", "DOESNOTEXISTB"],
        ignore_unresolved=True,
    )
    assert len(resolved) == 1
