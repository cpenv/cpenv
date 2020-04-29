# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
from collections import OrderedDict

# Local imports
from . import hooks, utils
from .module import Module, is_module, module_header
from .resolver import Resolver
from .vendor import yaml


__all__ = [
    'create',
    'publish',
    'remove',
    'resolve',
    'activate',
    'deactivate',
    'get_home_path',
    'get_user_path',
    'get_module_paths',
    'get_modules',
    'get_active_modules',
    'add_active_module',
    'remove_active_module',
]
_registry = {}
cpenv.api
=========
This module provides the main api for cpenv. Members of the api return models
which can be used to manipulate virtualenvs and modules. Members are available
directly from the cpenv namespace.
'''


def create(where, name, version, **kwargs):
    '''Create a new module.

    Arguments:
        where (str): Path to new module
        name (str): Name of module
        version (str): Version of module
        description (str): Optional description of module
        author (str): Optional author of module
        email (str): Optional email address of author
        requires (list): Optional modules that this module depends on
        environment (dict): Optional environment variables

    Returns:
        Module object
    '''

    # Setup configuration defaults
    config = OrderedDict([
        ('name', name),
        ('version', version),
        ('description', kwargs.get('description', '')),
        ('author', kwargs.get('author', '')),
        ('email', kwargs.get('email', '')),
        ('requires', kwargs.get('requires', [])),
        ('environment', kwargs.get('environment', {})),
    ])

    # Check if module already exists
    where = utils.normpath(where)
    if os.path.isdir(where):
        raise OSError('Module already exists at "%s"' % where)

    # Create a Module object - does not yet exist on disk
    module = Module(where, name, version)

    # Run global precreate hook
    # Allows users to inject data into a config prior to creating a new module
    hooks.run_global_hook('pre_create', module, config)

    # Create module folder structure
    utils.ensure_path_exists(where)
    utils.ensure_path_exists(where + '/hooks')

    data = module_header + yaml.dump(
        dict(config),
        default_flow_style=False,
        sort_keys=False,
    )
    with open(utils.normpath(where, 'module.yml'), 'w') as f:
        f.write(data)

    # Run global postcreate hook
    # Allows users to perform some action after a module is created
    hooks.run_global_hook('post_create', module)

    return


def publish(name_or_path=None, repository=None):
    '''Publish the module to the specified repository.'''


def remove(name_or_path):
    '''Remove an environment or module

    :param name_or_path: name or path to environment or module
    '''

    r = resolve(name_or_path)
    r.resolved[0].remove()


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
    return r.resolved


def deactivate():
    '''Deactivates an environment by restoring all env vars to a clean state
    stored prior to activating environments
    '''

    pass


def get_home_path():
    '''Returns $CPENV_HOME or ~/.cpenv'''

    home = utils.normpath(os.environ.get('CPENV_HOME', '~/.cpenv'))
    home_modules = utils.normpath(home, 'modules')

    if not os.path.exists(home):
        os.makedirs(home)

    if not os.path.exists(home_modules):
        os.makedirs(home_modules)

    return home


def get_user_path():
    '''Returns ~/.cpenv'''

    user = utils.normpath('~/.cpenv')
    user_modules = utils.normpath(user, 'modules')

    if not os.path.exists(user):
        os.makedirs(user)

    if not os.path.exists(user_modules):
        os.makedirs(user_modules)

    return user


def get_module_paths():
    '''Returns a list of paths used to lookup modules.

    The list of lookup paths contains:
        1. ~/.cpenv/modules
        2. $CPENV_HOME/modules
        3. $CPENV_MODULES
    '''

    module_paths = [utils.normpath(get_user_path(), 'modules')]

    cpenv_home_modules = utils.normpath(get_home_path(), 'modules')
    if cpenv_home_modules not in module_paths:
        module_paths.append(cpenv_home_modules)

    cpenv_modules_path = os.environ.get('CPENV_MODULES', None)
    if cpenv_modules_path:
        for module_path in cpenv_modules_path.split(os.pathsep):
            if module_path not in module_paths:
                module_paths.append(utils.normpath(module_path))

    return module_paths


def get_modules():
    '''Returns a list of available modules.'''

    modules = set()

    cwd = os.getcwd()
    for d in os.listdir(cwd):

        if d == 'module.yml':
            modules.add(Module(cwd))

        path = utils.normpath(cwd, d)
        if is_module(path):
            modules.add(Module(cwd))

    module_paths = get_module_paths()
    for module_path in module_paths:

        if not os.path.exists(module_path):
            continue

        for d in os.listdir(module_path):

            path = utils.normpath(module_path, d)
            if is_module(path):
                modules.add(Module(path))

    return sorted(list(modules), key=lambda x: x.name)


def register_repo(repo):
    '''Register a Repo.'''

    if repo not in _registry['repos']:
        _registry['repos'].append(repo)


def unregister_repo(repo):
    '''Unregister a Repo.'''

    if repo in _registry['repos']:
        _registry['repos'].pop(repo)
