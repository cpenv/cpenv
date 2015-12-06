# -*- coding: utf-8 -*-

from .models import VirtualEnvironment, Module
from .utils import unipath, is_environment
from .cache import EnvironmentCache
from .utils import join_dicts, set_env


class Resolver(object):
    '''Resolve, combine, activate VirtualEnvironment and Module environments.
    The args passed can follow two possible signatures.

    usage::

        >>> Resolver('production_env', 'module_a', 'module_b', 'module_c')

    If the first argument passed is a VirtualEnvironment, each additional arg
    is looked up relative to that VirtualEnvironment.

    OR::

        >>> Resolver('module_a', 'module_b', 'module_c')

    In this case the modules are looked up in the active VirtualEnvironment.

    :param cache: Optional keyword argument, cache for use with path resolvers

    '''

    def __init__(self, *args, **kwargs):

        if not args:
            raise ValueError('Resolver expects at least 1 argument.')

        self.paths = args
        self.cache = kwargs.get('cache', EnvironmentCache)
        self.resolved = None
        self.combined = None

    def resolve(self):

        self.resolved = []
        paths = list(self.paths)

        for resolver in resolvers:
            try:
                self.resolved.append(resolver(self, paths[0]))
                paths.pop(0)
                break
            except NameError:
                continue

        for path in paths:
            for resolver in module_resolvers:
                try:
                    self.resolved.append(resolver(self, path))
                    break
                except NameError:
                    continue
            else:
                raise NameError('Could not find an environment: ' + path)

        return self.resolved

    def combine(self):

        if not self.resolved:
            raise ValueError('You must call Resolver.resolve first.')

        return join_dicts(*[obj.environment for obj in self.resolved])

    def activate(self):

        set_env(self.combine())

        for obj in self.resolved:
            obj.activate()


def path_is_venv_resolver(resolver, path):
    '''Checks if path is already a VirtualEnvironment'''

    if isinstance(path, VirtualEnvironment):
        return path

    raise NameError


def path_resolver(resolver, path):
    '''Resolves VirtualEnvironments with a relative or absolute path'''

    path = unipath(path)

    if is_environment(path):
        return VirtualEnvironment(path)

    raise NameError


def home_resolver(resolver, path):
    '''Resolves VirtualEnvironments in CPENV_HOME'''

    from .api import get_home_path

    path = unipath(get_home_path(), path)

    if is_environment(path):
        return VirtualEnvironment(path)

    raise NameError


def cache_resolver(resolver, path):
    '''Resolves VirtualEnvironments in EnvironmentCache'''

    env = resolver.cache.find(path)
    if env:
        return env

    raise NameError


def path_is_module_resolver(resolver, path):
    '''Checks if path is already a :class:`Module` object'''

    if isinstance(path, Module):
        return path

    raise NameError


def module_resolver(resolver, path):
    '''Resolves module in previously resolved environment.'''

    if resolver.resolved:

        if isinstance(resolver.resolved[0], VirtualEnvironment):
            env = resolver.resolved[0]
            mod = env.get_module(path)

            if mod:
                return mod

    raise NameError


def active_env_module_resolver(resolver, path):
    '''Resolves modules in currently active environment.'''

    from .api import get_active_env

    env = get_active_env()
    if not env:
        raise NameError

    mod = env.get_module(path)
    if not mod:
        raise NameError

    return mod


resolvers = [
    path_is_venv_resolver,
    path_resolver,
    home_resolver,
    cache_resolver,
]

module_resolvers = [
    path_is_module_resolver,
    module_resolver,
    active_env_module_resolver,
]
