# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import warnings
from bisect import bisect
from collections import OrderedDict

# Local imports
from . import compat, hooks, paths, repos
from .module import Module, ModuleSpec, module_header, sort_modules
from .resolver import Activator, Copier, Localizer, ResolveError, Resolver
from .vendor import appdirs, yaml

__all__ = [
    'activate',
    'deactivate',
    'clone',
    'create',
    'localize',
    'publish',
    'resolve',
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
    'get_config_path',
    'read_config',
    'write_config',
    'update_repo',
    'remove_repo',
]
_registry = {
    'repos': OrderedDict(),
}
_active_modules = []
missing = object()


def resolve(requirements):
    '''Resolve a list of module requirements.'''

    resolver = Resolver(get_repos())
    return resolver.resolve(requirements)


def localize(requirements, to_repo='home', overwrite=False):
    '''Localize a list of requirements.'''

    to_repo = get_repo(to_repo)

    # Resolve modules
    resolver = Resolver(get_repos())
    module_specs = resolver.resolve(requirements)

    # Localize modules from remote repos
    localizer = Localizer(to_repo)
    modules = localizer.localize(module_specs, overwrite)

    return modules


def activate(requirements):
    '''Resolve and active a list of module requirements.

    Usage:
        >>> cpenv.activate('moduleA', 'moduleB')

    Arguments:
        requirements (List[str]): List of module requirements

    Returns:
        list of Module objects that have been activated
    '''

    # Resolve modules
    resolver = Resolver(get_repos())
    module_specs = resolver.resolve(requirements)

    # Activate modules
    activator = Activator()
    modules = activator.activate(module_specs)

    return modules


def activate_environment(environment):
    '''Activate an environment by name.

    Usage:
        >>> cpenv.activate_environment('MyEnvironment')

    Arguments:
        environment (str): Name of Environment

    Returns:
        list of Module objects that have been activated
    '''

    for repo in get_repos():
        for env in repo.list_environments():
            if env.name == environment:
                return activate(env.requires)
    else:
        raise ResolveError('Failed to resolve Environment: %s' % environment)


def deactivate():
    '''Deactivates an environment by restoring all env vars to a clean state
    stored prior to activating environments
    '''
    # TODO:
    # Probably need to store a clean environment prior to activate.
    # In practice it's uncommon to activate then deactivate in the same
    # python session.
    pass


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
    where = paths.normalize(where)
    if os.path.isdir(where):
        raise OSError('Module already exists at "%s"' % where)

    # Create a Module object - does not yet exist on disk
    module = Module(where, name, version)

    # Run global precreate hook
    # Allows users to inject data into a config prior to creating a new module
    hooks.run_global_hook('pre_create', module, config)

    # Create module folder structure
    paths.ensure_path_exists(where)
    paths.ensure_path_exists(where + '/hooks')

    data = module_header + yaml.dump(
        dict(config),
        default_flow_style=False,
        sort_keys=False,
    )
    with open(paths.normalize(where, 'module.yml'), 'w') as f:
        f.write(data)

    # Run global postcreate hook
    # Allows users to perform some action after a module is created
    hooks.run_global_hook('post_create', module)

    return module


def remove(module, from_repo=None):
    '''Remove a module.'''

    if isinstance(module, Module):
        return module.remove()

    if isinstance(module, ModuleSpec):
        return module.repo.remove(module)

    if from_repo is None:
        raise ValueError('from_repo is required when removing module by name.')

    if isinstance(from_repo, compat.string_types):
        from_repo = get_repo(from_repo)

    module_spec = from_repo.find(module)[0]
    return from_repo.remove(module_spec)


def clone(module, from_repo=None, where=None, overwrite=False):
    '''Clone a module for local development.

    A typical development workflow using clone and publish:
        1. clone a module
        2. make changes
        3. test changes
        4. increment version in module.yml
        5. publish a new version of your module
    '''

    if not isinstance(module, (Module, ModuleSpec)):
        if from_repo is None:
            resolver = Resolver(get_repos())
            module_spec = resolver.resolve([module])[0]
        else:
            from_repo = get_repo(from_repo)
            module_spec = from_repo.find(module)[0]

    module = module_spec.repo.download(
        module_spec,
        where=paths.normalize(where or '.', module_spec.real_name),
        overwrite=overwrite,
    )

    return module


def publish(module, to_repo='home', overwrite=False):
    '''Publish a module to the specified repository.'''

    to_repo = get_repo(to_repo)

    if isinstance(module, compat.string_types):
        resolver = Resolver(get_repos())
        module = resolver.resolve([module])[0]

    if isinstance(module, ModuleSpec):
        if not isinstance(module.repo, repos.LocalRepo):
            raise ValueError('Can only from modules in local repos.')
        else:
            module = Module(module.path)

    published = to_repo.upload(module, overwrite)
    return published


def copy(module, from_repo, to_repo, overwrite=False):
    '''Copy a module from one repo to another.'''

    from_repo = get_repo(from_repo)
    to_repo = get_repo(to_repo)

    # Resolve module
    resolver = Resolver([from_repo])
    module_spec = resolver.resolve([module])[0]

    copier = Copier(to_repo)
    copied = copier.copy([module_spec], overwrite)
    return copied


def get_active_modules():
    '''Returns a list of active :class:`Module` s'''

    return _active_modules


def add_active_module(module):
    '''Add a module to CPENV_ACTIVE_MODULES environment variable.

    Arguments:
        module (Module): Module to add to CPENV_ACTIVE_MODULES
    '''

    if module not in _active_modules:
        _active_modules.append(module)

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

    # Set new home path
    home = paths.normalize(path)
    os.environ['CPENV_HOME'] = home
    _init_home_path(home)

    # Add new LocalRepo
    update_repo(repos.LocalRepo('home', get_home_modules_path()))

    return home


def _init_home_path(home):
    folders = [
        home,
        paths.normalize(home, 'modules'),
        paths.normalize(home, 'environments'),
        paths.normalize(home, 'cache'),
    ]
    for folder in folders:
        paths.ensure_path_exists(folder)


def get_home_path():
    '''Returns the cpenv home directory.

    Default home paths:
        win - C:/ProgramData/cpenv
        mac - /Library/Application Support/cpenv OR /Library/Caches/cpenv
        linux - /usr/local/share/cpenv OR ~/.local/share/cpenv
    '''

    home = os.getenv('CPENV_HOME')
    if home and paths.is_writable(home):
        if paths.is_writable(home):
            return home
        else:
            raise RuntimeError('Could not access CPENV_HOME: %s', home)

    home_default = appdirs.site_data_dir('cpenv', appauthor=False)
    if paths.is_writable(home_default):
        return home_default
    else:
        if compat.platform == 'mac':
            # Fallback to /Library/Caches as it has open permissions
            # and it's still shared across all users. This is not ideal
            # however, people don't clear their cache often.
            fallback = '/Library/Caches/cpenv'
        elif compat.platform == 'linux':
            # Fallback to user directory on linux.
            fallback = appdirs.user_data_dir('cpenv', appauthor=False)
        else:
            raise RuntimeError('Could not access default home: %s', home)
        message = (
            'Could not access default cpenv home directory "{default}".'
            'Falling back to "{home}". If you want to use a shared home dir '
            'for all users on your machine run the following commands:\n\n'
            '    sudo mkdir {default}\n'
            '    sudo chmod -R a+rwx {default}\n'
        ).format(default=home_default, home=fallback)
        warnings.warn(message)
        return fallback


def get_home_modules_path():
    '''Return the modules directory within the cpenv home directory.'''

    return paths.normalize(get_home_path(), 'modules')


def get_cache_path(*parts):
    '''Return the cpenv cache directory within the cpenv home directory.

    Arguments:
        *parts (str) - List of path parts to join with cache path
    '''

    return paths.normalize(get_home_path(), 'cache', *parts)


def _init_user_path(user):
    '''Initialize user path.'''

    folders = [
        user,
        paths.normalize(user, 'modules'),
    ]
    for folder in folders:
        paths.ensure_path_exists(folder)


def get_user_path():
    '''Returns the cpenv user directory.

    Default user paths:
        win - C:/Users/<username>/AppData/Roaming/cpenv
        mac - ~/Library/Application Support/cpenv
        linux - ~/.local/share/cpenv
    '''

    user_default = appdirs.user_data_dir('cpenv', appauthor=False)
    user = paths.normalize(user_default)

    return user


def get_user_modules_path():
    '''Returns the modules directory within the cpenv user directory.

    Default user paths:
        win - C:/Users/<username>/AppData/Roaming/cpenv/modules
        mac - ~/Library/Application Support/cpenv/modules
        linux - ~/.local/share/cpenv/modules
    '''

    return paths.normalize(get_user_path(), 'modules')


def get_module_paths():
    '''Returns a list of paths used to lookup local modules.

    The list of lookup paths contains:
        1. use modules path
        2. home modules path
        3. paths in CPENV_MODULES environment variable
    '''

    module_paths = [paths.normalize(os.getcwd()), get_user_modules_path()]

    cpenv_home_modules = get_home_modules_path()
    if cpenv_home_modules not in module_paths:
        module_paths.append(cpenv_home_modules)

    cpenv_modules = os.environ.get('CPENV_MODULES', '').split(os.pathsep)
    for module_path in cpenv_modules:
        if module_path:
            module_paths.append(module_path)

    return module_paths


def add_module_path(path):
    '''Add an additional lookup path for local modules.'''

    path = paths.normalize(path)
    module_paths = []

    # Get existing module lookup paths
    cpenv_modules = os.environ.get('CPENV_MODULES', '').split(os.pathsep)
    for module_path in cpenv_modules:
        if module_path:
            module_paths.append(module_path)

    # Add new module lookup path
    if path not in module_paths:
        module_paths.append(path)
        add_repo(repos.LocalRepo(path, path))

    # Persist in CPENV_MODULES
    os.environ['CPENV_MODULES'] = os.pathsep.join(module_paths)

    return module_paths


def get_modules(*requirements):
    '''Returns a list of available modules.'''

    if requirements:
        resolver = Resolver(get_repos())
        return sort_modules(resolver.resolve(requirements))

    modules = []

    for repo in get_repos():
        modules.extend(repo.list())

    return sort_modules(list(modules))


def update_repo(repo):
    '''Update a registered repo.'''

    _registry['repos'].update({repo.name: repo})


def add_repo(repo, priority=None):
    '''Register a Repo.

    Arguments:
        priority (int): Override the Repos priority when adding.
    '''

    if priority is not None:
        repo.priority = priority

    if repo.name not in _registry['repos']:
        repos = list(_registry['repos'].values())
        insert_idx = bisect([r.priority for r in repos], repo.priority)
        if insert_idx == len(repos):
            _registry['repos'][repo.name] = repo
        else:
            repos.insert(insert_idx, repo)
            _registry['repos'] = OrderedDict([(repo.name, repo) for repo in repos])


def remove_repo(repo):
    '''Unregister a Repo.'''

    _registry['repos'].pop(repo.name, None)


def get_repo(name, **query):
    '''Get a repo by specifying an attribute to lookup'''

    if isinstance(name, repos.Repo):
        return name

    query['name'] = name

    for repo in get_repos():
        if all([getattr(repo, k, False) == v for k, v in query.items()]):
            return repo


def get_repos():
    '''Get a list of all registered Repos.'''

    return list(_registry['repos'].values())


def get_config_path():
    return paths.normalize(get_home_path(), 'config.yml')


def read_config(key=None, default=missing):
    '''Read the whole config or a specific key from disk.

    Examples:
        # Read whole config
        config = read_config()

        # Read one key
        repos = read_config('repos', {})
    '''

    config_path = get_config_path()
    if not os.path.isfile(config_path):
        return {}

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f.read()) or {}

    if not key:
        return config

    config_key = config.get(key, missing)
    if config_key is missing:
        if default is missing:
            raise KeyError('Config has no key: ' + key)
        else:
            return default

    return config_key


def write_config(*args):
    '''Write the whole config or a specific key to disk.

    Examples:
        # Write whole config
        write_config({'repos': {}})

        # Write one config key
        write_config('repos', {})
    '''
    if len(args) == 1:
        config = args[0]
    elif len(args) == 2:
        config = read_config()
        config[args[0]] = args[1]
    else:
        raise ValueError('Expected 1 or 2 arguments got %s' % len(args))

    config_path = get_config_path()
    with open(config_path, 'w') as f:
        f.write(yaml.dump(config))


def _init():
    '''Responsible for initially configuraing cpenv.'''

    _init_home_path(get_home_path())
    _init_user_path(get_user_path())

    # Register builtin repos
    cwd = repos.LocalRepo('cwd', paths.normalize(os.getcwd()))
    user = repos.LocalRepo('user', get_user_modules_path())
    home = repos.LocalRepo('home', get_home_modules_path())
    if cwd.path == home.path == user.path:
        builtin_repos = [home]
    elif cwd.path == home.path:
        builtin_repos = [home, user]
    elif cwd.path == user.path:
        builtin_repos = [user, home]
    elif user.path == home.path:
        builtin_repos = [cwd, home]
    else:
        builtin_repos = [cwd, user, home]
    for repo in builtin_repos:
        add_repo(repo)

    # Register additional repos from CPENV_MODULE_PATHS
    builtin_module_paths = [repo.path for repo in get_repos()]
    for path in get_module_paths():
        if path in builtin_module_paths:
            continue
        add_repo(repos.LocalRepo(path, path))

    # Register repos from config
    configured_repos = read_config('repos', {})
    for name, config in configured_repos.items():
        repo_type = config.pop('type')
        repo_cls = repos.registry[repo_type]
        try:
            add_repo(repo_cls(**config))
        except Exception as e:
            warnings.warn('Failed to create %s repo named %s\nError: %s' % (
                repo_type,
                config['name'],
                str(e),
            ))

    # Set _active_modules from CPENV_ACTIVE_MODULES
    unresolved = []
    resolver = Resolver(get_repos())
    active_modules = os.getenv('CPENV_ACTIVE_MODULES', '').split(os.pathsep)
    for module in active_modules:
        if module:
            try:
                resolved = resolver.resolve([module])[0]
                _active_modules.append(resolved)
            except ResolveError:
                unresolved.append(module)

    if unresolved:
        warnings.warn(
            'Unable to resolve %s from $CPENV_ACTIVE_MODULES:' % unresolved
        )
