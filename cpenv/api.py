# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import sys
from collections import OrderedDict

# Local imports
from . import hooks, utils
from .module import Module, module_header
from .repos import LocalRepo
from .resolver import Resolver
from .vendor import appdirs, yaml


__all__ = [
    'create',
    'publish',
    'remove',
    'resolve',
    'activate',
    'deactivate',
    'set_home_path',
    'get_home_path',
    'get_home_modules_path',
    'get_cache_path',
    'get_user_path',
    'get_user_modules_path',
    'get_modules',
    'get_module_paths',
    'add_module_path',
    'get_active_modules',
    'add_active_module',
    'remove_active_module',
    'get_repos',
    'get_repo',
    'add_repo',
    'remove_repo',
    'sort_modules',
]
this = sys.modules[__name__]
_registry = {
    'repos': [],
}
_active_modules = []


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


def publish(module, to_repo='home', overwrite=False):
    '''Publish a module to the specified repository.'''

    if not isinstance(to_repo, Repo):
        to_repo = get_repo(name=to_repo)

    if not isinstance(module, (Module, ModuleSpec)):
        module_ = Module(module)
        if not module_:
            raise ResolveError(
                'Failed to resolve %s in %s' % (module, to_repo.name)
            )
        module = module_

    published_module = to_repo.publish_module(module, overwrite)
    return published_module


def remove(module, from_repo=None):
    '''Remove a module from the specified repository.

    Arguments:
        module (Module, ModuleSpec, or str): Module to remove
        from_repo (Repo or str): Repository to remove the module from
    '''

    # A Module is always local and can be removed outright
    if isinstance(module, Module):
        module.remove()
        return

    # A ModuleSpec has a reference to it's repo
    if isinstance(module, ModuleSpec):
        module.repo.remove(module)
        return

    # Typecheck arguments
    if not isinstance(module, compat.string_types):
        raise ValueError('module must be a Module, ModuleSpec or string')

    if from_repo is None:
        raise ValueError(
            'You must specify from_repo when passing module as a string'
        )

    if not isinstance(from_repo, Repo):
        from_repo = get_repo(name=from_repo)

    # Find a Module or ModuleSpec
    module_ = module
    module = from_repo.find_module(module)

    if not module:
        raise ResolveError('Could not find %s in %s' % (module_, from_repo))

    if isinstance(module, Module):
        module.remove()
        return

    if isinstance(module, ModuleSpec):
        module.repo.remove(module)
        return


def localize(*modules, to_repo='home', overwrite=False):
    '''Localize a list of modules.'''

    if not isinstance(to_repo, Repo):
        to_repo = get_repo(name=to_repo)

    resolver = resolve(*modules)
    resolver.localize(to_repo, overwrite)
    return resolver.modules


def resolve(*modules):
    '''Resolve a list of modules and return a :class:`Resolver` instance.'''

    resolver = Resolver(*modules)
    resolver.resolve()
    return resolver


def activate(*modules):
    '''Resolve and active a list of modules.

    Usage:
        >>> cpenv.activate('moduleA', 'moduleB')

    Arguments:
        modulues (List[str, Module]): List of string or

    Returns:
        list of Module objects that have been activated
    '''

    resolver = resolve(*modules)
    resolver.activate()
    return resolver.resolved


def deactivate():
    '''Deactivates an environment by restoring all env vars to a clean state
    stored prior to activating environments
    '''

    pass


def get_active_modules(resolve=False):
    '''Returns a list of active :class:`Module` s'''

    if not _active_modules or not resolve:
        return _active_modules

    resolver = this.resolve(*_active_modules)
    return resolver.resolved


def add_active_module(module):
    '''Add a module to CPENV_ACTIVE_MODULES environment variable.

    Arguments:
        module (Module): Module to add to CPENV_ACTIVE_MODULES
    '''

    if module not in _active_modules:
        _active_modules.append(module)

    _active_modules.sort(key=lambda m: m.real_name)

    module_names = os.pathsep.join([m.real_name for m in _active_modules])
    os.environ['CPENV_ACTIVE_MODULES'] = str(module_names)


def remove_active_module(module):
    '''Remove a module from CPENV_ACTIVE_MODULES environment variable.

    Arguments:
        module (Module): Module to remove from CPENV_ACTIVE_MODULES
    '''

    if module in _active_modules:
        _active_modules.remove(module)

    module_names = os.pathsep.join([m.real_name for m in _active_modules])
    os.environ['CPENV_ACTIVE_MODULES'] = str(module_names)


def set_home_path(path):
    '''Convenient function used to set the CPENV_HOME environment variable.'''

    # Remove old LocalRepo
    remove_repo(LocalRepo(get_home_modules_path()))

    # Set new home path
    home = utils.normpath(path)
    os.environ['CPENV_HOME'] = home
    _init_home_path(home)

    # Add new LocalRepo
    add_repo(LocalRepo(get_home_modules_path()))

    return home


def _init_home_path(home):
    home_modules = utils.normpath(home, 'modules')
    home_cache = utils.normpath(home, 'cache')

    utils.ensure_path_exists(home)
    utils.ensure_path_exists(home_modules)
    utils.ensure_path_exists(home_cache)


def get_home_path():
    '''Returns the cpenv home directory.

    Default home paths:
        win - C:/ProgramData/cpenv
        mac - /Library/Application Support/cpenv
        linux - /usr/local/share/cpenv OR /usr/share/cpenv
    '''

    home_default = appdirs.site_data_dir('cpenv', appauthor=False)
    home = utils.normpath(os.getenv('CPENV_HOME', home_default))
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


def _init_user_path(user):
    '''Initialize user path.'''

    user_modules = utils.normpath(user, 'modules')
    utils.ensure_path_exists(user)
    utils.ensure_path_exists(user_modules)


def get_user_path():
    '''Returns the cpenv user directory.

    Default user paths:
        win - C:/Users/<username>/AppData/Roaming/cpenv
        mac - ~/Library/Application Support/cpenv
        linux - ~/.local/share/cpenv
    '''

    user_default = appdirs.user_data_dir('cpenv', appauthor=False)
    user = utils.normpath(user_default)

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

    module_paths = [utils.normpath(os.getcwd()), get_user_modules_path()]

    cpenv_home_modules = get_home_modules_path()
    if cpenv_home_modules not in module_paths:
        module_paths.append(cpenv_home_modules)

    cpenv_modules_path = os.environ.get('CPENV_MODULES', None)
    if cpenv_modules_path:
        for module_path in cpenv_modules_path.split(os.pathsep):
            if module_path not in module_paths:
                module_paths.append(utils.normpath(module_path))

    return module_paths


def add_module_path(path):
    '''Add an additional lookup path for local modules.'''

    path = utils.normpath(path)
    module_paths = []

    # Get existing module lookup paths
    cpenv_modules = os.environ.get('CPENV_MODULES', '').split(os.pathsep)
    for module_path in cpenv_modules:
        if module_path:
            module_paths.append(module_path)

    # Add new module lookup path
    if path not in module_paths:
        module_paths.append(path)
        add_repo(LocalRepo(path))

    # Persist in CPENV_MODULES
    os.environ['CPENV_MODULES'] = os.pathsep.join(module_paths)

    return module_paths


def get_modules():
    '''Returns a list of available modules.'''

    modules = []

    for repo in get_repos():
        modules.extend(repo.list_modules())

    return sort_modules(list(modules))


def add_repo(repo):
    '''Register a Repo.'''

    if repo not in this._registry['repos']:
        this._registry['repos'].append(repo)


def remove_repo(repo):
    '''Unregister a Repo.'''

    if repo in this._registry['repos']:
        this._registry['repos'].remove(repo)


def get_repo(**query):
    '''Get a repo by specifying an attribute to lookup'''

    if not query:
        raise ValueError('Expected an attribute lookup.')

    for repo in get_repos():
        if all([getattr(repo, k, None) == v for k, v in query.items()]):
            return repo


def get_repos():
    '''Get a list of all registered Repos.'''

    return list(this._registry['repos'])


def sort_modules(modules, reverse=False):
    return sorted(
        modules,
        key=lambda m: (m.real_name, m.version),
        reverse=reverse
    )


def _init():
    '''Responsible for initially configuraing cpenv.'''

    _init_home_path(get_home_path())
    _init_user_path(get_user_path())

    # Register all LocalRepos
    for path in get_module_paths():
        add_repo(LocalRepo(path))

    # Set _active_modules from CPENV_ACTIVE_MODULES
    active_modules = os.getenv('CPENV_ACTIVE_MODULES')
    if active_modules:
        for module in active_modules.split(os.pathsep):
            if module:
                _active_modules.append(module)
