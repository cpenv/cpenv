# -*- coding: utf-8 -*-

import os
import sys
from functools import partial
import mock
import virtualenv
from cpenv.utils import rmtree, unipath
from cpenv.log import logger
import cpenv

data_path = partial(os.path.join, os.path.dirname(__file__), 'data')


# Mock some stuff
class MockGit(cpenv.deps.Git):

    REPOS = [
        'https://github.com/cpenv/template_module.git'
    ]

    def clone(self, repo_path, destination, branch=None):

        logger.debug('Mock clone ' + repo_path)
        if repo_path not in self.REPOS:
            return False

        if not destination.startswith(self.env_path):
            destination = unipath(self.env_path, destination)

        if not os.path.exists(destination):
            os.makedirs(destination)
            return True

        return False

    def pull(self, repo_path, *args):
        logger.debug('Mock pull')
        return True


class MockPip(cpenv.deps.Pip):

    def wheel(self, package):
        pass

    def install(self, package):
        logger.debug('Mock installing ' + package)

    def upgrade(self, package):
        logger.debug('Mock upgrading ' + package)


def mock_create_environment(env_path):
    logger.debug('IN MOCK CREATE ENVIRONMENT')
    if cpenv.platform == 'win':
        os.makedirs(unipath(env_path, 'Scripts'))
        os.makedirs(unipath(env_path, 'Lib', 'site-packages'))
        return

    py_ver = 'python{0}'.format(sys.version[:3])
    os.makedirs(unipath(env_path, 'lib', py_ver, 'site-packages'))
    os.makedirs(unipath(env_path, 'bin'))


def patch_stuff():
    cpenv.deps.Git = MockGit
    cpenv.deps.Pip = MockPip
    virtualenv.create_environment = mock_create_environment


def setup_package():
    patch_stuff()
    os.environ['CPENV_HOME'] = data_path('home')


def teardown_package():
    rmtree(data_path())
    pass
