# -*- coding: utf-8 -*-

# Standard library imports
import os
import sys

# Local imports
import cpenv
from cpenv.utils import normpath, rmtree

# Local imports
from .utils import touch


def data_path(*args):
    return normpath(os.path.dirname(__file__), 'data', *args)


# Mock some stuff
class MockGit(cpenv.deps.Git):

    REPOS = [
        'https://github.com/cpenv/template_module.git'
    ]

    def clone(self, repo_path, destination, branch=None):

        if repo_path not in self.REPOS:
            return False

        if not destination.startswith(self.env_path):
            destination = normpath(self.env_path, destination)

        if not os.path.exists(destination):
            os.makedirs(destination)
            touch(normpath(destination, 'module.yml'))
            return True

        return False

    def pull(self, repo_path, *args):
        return True


class MockPip(cpenv.deps.Pip):

    def wheel(self, package):
        pass

    def install(self, package):
        pass

    def upgrade(self, package):
        pass


def mock_create_environment(env_path):
    if cpenv.platform == 'win':
        os.makedirs(normpath(env_path, 'Scripts'))
        os.makedirs(normpath(env_path, 'Lib', 'site-packages'))
        return

    py_ver = 'python{0}'.format(sys.version[:3])
    os.makedirs(normpath(env_path, 'lib', py_ver, 'site-packages'))
    os.makedirs(normpath(env_path, 'bin'))


def patch_stuff():
    cpenv.deps.Git = MockGit
    cpenv.deps.Pip = MockPip


def setup_package():
    patch_stuff()
    cpenv.set_home_path(data_path('home'))


def teardown_package():
    rmtree(data_path())
