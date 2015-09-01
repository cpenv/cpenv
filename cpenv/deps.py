import subprocess
import logging
import shutil
import os
from . import platform
from .utils import unipath

logger = logging.getLogger('cpenv')


def get_pip_path():
    '''Returns path to pip for current environment'''

    from .api import get_active_env
    active_env = get_active_env()
    if active_env:
        if platform == 'win':
            return unipath(active_env, 'Scripts', 'pip')
        return unipath(active_env, 'bin', 'pip')
    return 'pip'


def pip_install(package):
    '''Quietly install a python package using pip'''

    cmd_args = [get_pip_path(), '-q', 'install', package]
    try:
        subprocess.check_call(cmd_args, env=os.environ, shell=True)
        logger.debug('pip installed ' + package)
    except subprocess.CalledProcessError:
        logger.debug('pip failed to install ' + package)


def git_clone(repo, destination):
    '''Clone a repository to the specified path'''

    cmd_args = ['git', 'clone', '-q', repo, destination]
    try:
        subprocess.check_call(cmd_args, env=os.environ, shell=True)
        logger.debug('cloned {} to {}'.format(repo, destination))
    except subprocess.CalledProcessError:
        logger.debug('git failed to clone ' + repo)


def copy_tree(source, destination):
    '''Copy a tree to the specified path'''

    try:
        shutil.copytree(source, destination)
    except:
        logger.debug('Failed to include ' + source)
