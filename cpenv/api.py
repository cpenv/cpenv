# -*- coding: utf-8 -*-
'''
cpenv.api
=========
This module provides the main api for cpenv. Members of the api return models
which can be used to manipulate virtualenvs and modules. Members are available
directly from the cpenv namespace.
'''

import os
import virtualenv
import shutil
from .log import logger
from .cache import EnvironmentCache
from .resolver import Resolver
from .utils import unipath
from .models import VirtualEnvironment, Module
from .deps import Git
from . import utils, defaults


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

    env = VirtualEnvironment(path)
    utils.ensure_path_exists(env.path)

    if config:
        if utils.is_git_repo(config):
            Git('').clone(config, env.path)
        else:
            shutil.copy2(config, env.config_path)
    else:
        with open(env.config_path, 'w') as f:
            f.write(defaults.environment_config)

    utils.ensure_path_exists(env.hook_path)
    utils.ensure_path_exists(env.modules_path)

    env.run_hook('precreate')

    virtualenv.create_environment(env.path)
    if not utils.is_home_environment(env.path):
        EnvironmentCache.add(env)
        EnvironmentCache.save()

    try:
        env.update()
    except Exception:
        utils.rmtree(path)
        logger.debug('Failed to update, rolling back...')
        raise
    else:
        env.run_hook('postcreate')

    return env


def remove(name_or_path):
    '''Remove an environment or module

    :param name_or_path: name or path to environment or module
    '''

    r = resolve(name_or_path)
    r.resolved[0].remove()

    EnvironmentCache.discard(r.resolved[0])
    EnvironmentCache.save()


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
    :returns: :class:`VirtualEnv` instance of active environment
    '''

    r = resolve(*args)
    r.activate()
    return get_active_env()


def launch(module_name, *args, **kwargs):
    '''Activates and launches a module

    :param module_name: name of module to launch
    '''

    r = resolve(module_name)
    r.activate()
    mod = r.resolved[0]
    mod.launch(*args, **kwargs)


def deactivate():
    '''Deactivates an environment by restoring all env vars to a clean state
    stored prior to activating environments
    '''

    if 'CPENV_ACTIVE' not in os.environ or 'CPENV_CLEAN_ENV' not in os.environ:
        raise EnvironmentError('Can not deactivate environment...')

    utils.restore_env_from_file(os.environ['CPENV_CLEAN_ENV'])


def get_home_path():
    ''':returns: your home path...CPENV_HOME env var OR ~/.cpenv'''

    home = unipath(os.environ.get('CPENV_HOME', '~/.cpenv'))
    home_modules = unipath(home, 'modules')
    if not os.path.exists(home):
        os.makedirs(home)
    if not os.path.exists(home_modules):
        os.makedirs(home_modules)
    return home


def get_module_paths():
    ''':returns: paths in CPENV_MODULES env var and CPENV_HOME/modules'''

    module_paths = []

    cpenv_modules_path = os.environ.get('CPENV_MODULES', None)
    if cpenv_modules_path:
        module_paths.extend(cpenv_modules_path.split(os.pathsep))

    module_paths.append(unipath(get_home_path(), 'modules'))

    return module_paths


def get_active_env():
    ''':returns: the active environment as a :class:`VirtualEnvironment`
    instance or None if one is not active.
    '''

    active = os.environ.get('CPENV_ACTIVE', None)
    if active:
        return VirtualEnvironment(active)


def get_environment(name_or_path):
    '''Get a :class:`VirtualEnvironment` by name or path.'''

    r = resolve(name_or_path)
    return r.resolved[0]


def get_environments():
    '''Returns a list of all known virtual environments as
    :class:`VirtualEnvironment` instances. This includes those in CPENV_HOME
    and any others that are cached(created by the current user or activated
    once by full path.)
    '''

    environments = set()

    cwd = os.getcwd()
    for d in os.listdir(cwd):

        if d == 'environment.yml':
            environments.add(VirtualEnvironment(cwd))
            continue

        path = unipath(cwd, d)
        if utils.is_environment(path):
            environments.add(VirtualEnvironment(path))

    home = get_home_path()
    for d in os.listdir(home):

        path = unipath(home, d)
        if utils.is_environment(path):
            environments.add(VirtualEnvironment(path))

    for env in EnvironmentCache:
        environments.add(env)

    return sorted(list(environments), key=lambda x: x.name)


def get_modules():
    '''Returns a list of available modules.'''

    modules = set()

    cwd = os.getcwd()
    for d in os.listdir(cwd):

        if d == 'module.yml':
            modules.add(Module(cwd))

        path = unipath(cwd, d)
        if utils.is_module(path):
            modules.add(Module(cwd))

    module_paths = get_module_paths()
    for module_path in module_paths:
        for d in os.listdir(module_path):

            path = unipath(module_path, d)
            if utils.is_module(path):
                modules.add(Module(path))

    return sorted(list(modules), key=lambda x: x.name)


def get_active_modules():
    ''':returns: a list of active :class:`Module` s or []'''

    modules = os.environ.get('CPENV_ACTIVE_MODULES', None)
    if modules:
        modules = modules.split(os.pathsep)
        return [Module(module) for module in modules]

    return []


def add_active_module(module):
    '''Add a module to CPENV_ACTIVE_MODULES environment variable'''

    modules = set(get_active_modules())
    modules.add(module)
    new_modules_path = os.pathsep.join([m.path for m in modules])
    os.environ['CPENV_ACTIVE_MODULES'] = str(new_modules_path)


def rem_active_module(module):
    '''Remove a module from CPENV_ACTIVE_MODULES environment variable'''

    modules = set(get_active_modules())
    modules.discard(module)
    new_modules_path = os.pathsep.join([m.path for m in modules])
    os.environ['CPENV_ACTIVE_MODULES'] = str(new_modules_path)


def create_module(name_or_path, config=None, branch=None):
    '''Create a new module.

    Optionally specify a config which can be a git repo. If the config is a git
    repo you can specify a branch as well.

    :param name_or_path: Name or full path of environment
    :param config: Environment configuration including dependencies etc...
    :param branch: If config is a git repo, use this branch
    '''

    # Get the real path of the module
    if utils.is_system_path(name_or_path):
        path = unipath(name_or_path)
    else:
        path = unipath('.', name_or_path)

    if os.path.exists(path):
        raise OSError('{} already exists'.format(path))

    utils.ensure_path_exists(path)
    module = Module(path)

    if config:
        if utils.is_git_repo(config):
            Git('').clone(config, module.path, branch)
        elif utils.is_module(config):
            shutil.copytree(unipath(config), module.path)
        elif os.path.isfile(config) and config.endswith('.yml'):
            utils.ensure_path_exists(module.path)
            shutil.copy2(config, module.config_path)
        else:
            raise Exception('Config must be a repo, module, or config_path.')
    else:
        with open(module.config_path, 'w') as f:
            f.write(defaults.module_config)

    utils.ensure_path_exists(module.hook_path)
    module.run_hook('precreatemodule')
    module.run_hook('postcreatemodule')

    return module
