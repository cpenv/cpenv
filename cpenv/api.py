# -*- coding: utf-8 -*-

import os
import virtualenv
import shutil
from .cache import EnvironmentCache
from .resolver import Resolver
from .utils import unipath, touch
from .models import VirtualEnvironment
from .hooks import run_global_hook
from . import utils


def create(name_or_path=None, config=None):
    '''Create a virtual environment. You can pass either the name of a new
    environment to create in your CPENV_HOME directory OR specify a full path
    to create an environment outisde your CPENV_HOME.

    Create an environment in CPENV_HOME::

        >>> cpenv.create('myenv')

    Create an environment elsewhere::

        >>> cpenv.create('~/custom_location/myenv')

    :param name_or_path: Name or full path of environment
    :param config: Environment configuration including dependencies etc...
    '''

    # Get the real path of the environment
    if utils.is_system_path(name_or_path):
        path = unipath(name_or_path)
    else:
        path = unipath(get_home_path(), name_or_path)

    if os.path.exists(path):
        raise OSError('{} already exists'.format(path))

    os.makedirs(path)

    # Create hooks and modules folders
    for d in ['hooks', 'modules']:
        os.mkdir(unipath(path, d))

    # Copy config file into environment
    config_path = unipath(path, 'environment.yml')
    if not config:
        touch(config_path)
    else:
        shutil.copy2(config, config_path)

    env = VirtualEnvironment(path)

    run_global_hook('precreate', env)

    virtualenv.create_environment(env.path)
    if not utils.is_home_environment(env.path):
        EnvironmentCache.add(env)

    try:
        env.update()
    except:
        shutil.rmtree(path)
        raise

    run_global_hook('postcreate', env)

    return env


def resolve(*args):
    '''Resolve a list of virtual environment and module names then return
    a :class:`Resolver` instance.'''

    r = Resolver(*args)
    r.resolve()
    return r


def activate(*args):
    '''Activate a virtual environment by name or path. Additional args refer
    to modules residing in the specified environment that you would
    also like to activate.

    Activate an environment::

        >>> cpenv.activate('myenv')

    Activate an environment with some modules::

        >>> cpenv.activate('myenv', 'maya', 'mtoa', 'vray_for_maya')

    :param name_or_path: Name or full path of environment
    :param modules: Additional modules to activate
    '''

    r = resolve(*args)
    r.activate()
    return get_active_env()


def deactivate():
    '''Deactivates an environment by restoring all env vars to a clean state
    stored prior to activating environments
    '''

    if 'CPENV_ACTIVE' not in os.environ:
        return
    if 'CPENV_CLEAN_ENV' not in os.environ:
        raise EnvironmentError('Can not deactivate environment...')

    utils.restore_env_from_file(os.environ['CPENV_CLEAN_ENV'])


def get_home_path():
    '''Returns your home path...CPENV_HOME env var OR ~/.cpenv'''

    home = unipath(os.environ.get('CPENV_HOME', '~/.cpenv'))
    if not os.path.exists(home):
        os.makedirs(home)
    return home


def get_active_env():
    '''Returns the active environment as a VirtualEnvironment instance or
    None if one is not active.
    '''

    active = os.environ.get('CPENV_ACTIVE', None)
    if active:
        return VirtualEnvironment(active)


def get_environments():
    '''Returns a list of all known virtual environments as VirtualEnvironment
    instances. This includes those in CPENV_HOME and any others that are
    cached(created by the current user or activated once by full path.)
    '''

    environments = []

    cwd = os.getcwd()
    for d in os.listdir(cwd):

        if d == 'environment.yml':
            environments.append(VirtualEnvironment(cwd))
            continue

        path = unipath(cwd, d)
        if utils.is_environment(path):
            environments.append(VirtualEnvironment(path))

    home = get_home_path()
    for d in os.listdir(home):

        path = unipath(home, d)
        if utils.is_environment(path):
            environments.append(VirtualEnvironment(path))

    for env in EnvironmentCache:
        environments.append(env)

    return environments


def get_environment(name_or_path):
    '''Get a :class:`VirtualEnvironment` by name or path.'''

    r = resolve(name_or_path)
    return r.resolved[0]
