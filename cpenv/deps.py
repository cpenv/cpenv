# -*- coding: utf-8 -*-

from . import shell
from .log import logger
from .utils import unipath, walk_dn


class Git(object):
    '''Wrapped Git Commands'''

    def __init__(self, env_path):
        self.env_path = env_path

    def find_repos(self, depth=10):
        '''Get all git repositories within this environment'''

        repos = []

        for root, subdirs, files in walk_dn(self.root, depth=depth):
            if 'modules' in root:
                continue
            if '.git' in subdirs:
                repos.append(root)

        return repos

    def clone(self, repo_path, destination, branch=None):
        '''Clone a repository to a destination relative to envrionment root'''

        logger.debug('Installing ' + repo_path)
        if not destination.startswith(self.env_path):
            destination = unipath(self.env_path, destination)

        if branch:
            return shell.run('git', 'clone', repo_path,
                             '--branch', branch, '--single-branch',
                             destination)

        return shell.run('git', 'clone', repo_path, destination)

    def pull(self, repo_path, *args):
        '''Clone a repository to a destination relative to envrionment root'''

        logger.debug('Pulling ' + repo_path)
        if not repo_path.startswith(self.env_path):
            repo_path = unipath(self.env_path, repo_path)

        return shell.run('git', 'pull', *args, **{'cwd': repo_path})


class Pip(object):
    '''Wrapped Pip Commands'''

    def __init__(self, pip_path):
        self.pip_path = str(pip_path)

    def wheel(self, package):
        '''pip wheel it'''

        shell.run(self.pip_path, 'wheel', package)

    def install(self, package):
        '''Install a python package using pip'''

        logger.debug('Installing ' + package)
        shell.run(self.pip_path, 'install', package)

    def upgrade(self, package):
        '''Update a python package using pip'''

        logger.debug('Upgrading ' + package)
        shell.run(self.pip_path, 'install', '--upgrade', '--no-deps', package)
        shell.run(self.pip_path, 'install', package)
