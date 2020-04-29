# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
from collections import OrderedDict

# Local imports
from . import hooks, utils
from .module import Module, is_module, module_header
from .resolver import Resolver
from .vendor import yaml, appdirs


__all__ = [
    'create',
    'publish',
    'remove',
    'resolve',
    'activate',
    'deactivate',
    'get_home_path',
    'get_home_modules_path',
    'get_cache_path',
    'get_user_path',
    'get_user_modules_path',
    'get_modules',
    'get_module_paths',
    'get_active_modules',
    'add_active_module',
    'remove_active_module',
]
_registry = {}


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


def clone(module, where='.', repo=None):
    '''Clone a module.

    Useful for development. One might do something like:
        1. clone a module
        2. make changes
        3. test changes
        3. publish a new version of the module
    '''


def publish(module, repo=None):
    '''Publish a module to the specified repository.'''


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




def set_home_path(path):
    '''Convenient function used to set the CPENV_HOME environment variable.'''

    os.environ['CPENV_HOME'] = path


def get_home_path():
    '''Returns the cpenv home directory.

    Default home paths:
        win - C:/ProgramData/cpenv
        mac - /Library/Application Support/cpenv
        linux - /usr/local/share/cpenv OR /usr/share/cpenv
    '''

    home_default = appdirs.site_data_dir('cpenv', appauthor=False)
    home = utils.normpath(os.getenv('CPENV_HOME', home_default))
    home_modules = utils.normpath(home, 'modules')
    home_cache = utils.normpath(home, 'cache')

    utils.ensure_path_exists(home)
    utils.ensure_path_exists(home_modules)
    utils.ensure_path_exists(home_cache)

    return home


def get_home_modules_path():
    '''Return the modules directory within the cpenv home directory.

    Default home modules paths:
        win - C:/ProgramData/cpenv/modules
        mac - /Library/Application Support/cpenv/modules
        linux - /usr/local/share/cpenv OR /usr/share/cpenv/modules
    '''

    return utils.normpath(get_home_path(), 'modules')


def get_cache_path(*paths):
    '''Return the cpenv cache directory within the cpenv home directory.

    Default cache paths:
        win - C:/ProgramData/cpenv/cache
        mac - /Library/Application Support/cpenv/cache
        linux - /usr/local/share/cpenv OR /usr/share/cpenv/cache

    Arguments:
        *paths (str) - List of paths to join with cache path
    '''

    return utils.normpath(get_home_path(), 'cache', *paths)


def get_user_path():
    '''Returns the cpenv user directory.

    Default user paths:
        win - C:/Users/<username>/AppData/Roaming/cpenv
        mac - ~/Library/Application Support/cpenv
        linux - ~/.local/share/cpenv
    '''

    user_default = appdirs.user_data_dir('cpenv', appauthor=False)
    user = utils.normpath(user_default)
    user_modules = utils.normpath(user, 'modules')

    utils.ensure_path_exists(user)
    utils.ensure_path_exists(user_modules)

    return user


def get_user_modules_path():
    '''Returns the modules directory within the cpenv user directory.

    Default user paths:
        win - C:/Users/<username>/AppData/Roaming/cpenv/modules
        mac - ~/Library/Application Support/cpenv/modules
        linux - ~/.local/share/cpenv/modules
    '''

    return utils.normpath(get_user_path(), 'modules')


def get_module_paths():
    '''Returns a list of paths used to lookup local modules.

    The list of lookup paths contains:
        1. use modules path
        2. home modules path
        3. paths in CPENV_MODULES environment variable
    '''

    module_paths = [get_user_modules_path()]

    cpenv_home_modules = get_home_modules_path()
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
