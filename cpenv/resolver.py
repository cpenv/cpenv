# -*- coding: utf-8 -*-
'''
cpenv.resolver
==============
Defines :class:`Resolver` used to resolve cpenv :class:`VirtualEnvironment` s and :class:`Module` s
'''
import os
from .models import VirtualEnvironment, Module
from .utils import (unipath, is_environment, is_module, join_dicts,
                    set_env, walk_up, is_redirecting, redirect_to_env_paths)


class ResolveError(Exception):
    pass


class Resolver(object):
    '''Resolve, combine, and activate :class:`VirtualEnvironment`s and
    class:`Module`s.

    Each argument should be the name or path of a VirtualEnvironment or Module
    resolve. VirtualEnvironments will be looked up using the resolver functions
    in the cpenv.resolver.resolvers list. Modules will be looked up using
    the resolver functions in the cpenv.resolver.module_resolvers list. In both
    cases the first resolver to return a resolved file path will be used.

    usage::

        >>> Resolver('production_env', 'module_a', 'module_b', 'module_c')
    '''

    def __init__(self, *paths):

        if not paths:
            raise ValueError('Resolver expects at least 1 argument.')

        self.paths = paths
        self.resolved = None
        self.combined = None

    def resolve(self):

        self.resolved = []
        paths = list(self.paths)

        for resolver in resolvers:
            try:

                resolved = resolver(self, paths[0])

                if isinstance(resolved, VirtualEnvironment):
                    self.resolved.append(resolved)
                    paths.pop(0)

                elif isinstance(resolved, list):
                    self.resolved.extend(resolved)
                    paths.pop(0)

                break

            except ResolveError:
                continue

        for path in paths:
            for resolver in module_resolvers:
                try:

                    resolved = resolver(self, path)

                    if isinstance(resolved, Module):
                        self.resolved.append(resolved)

                    elif isinstance(resolved, list):
                        self.resolved.extend(resolved)

                    break

                except ResolveError:
                    continue
            else:
                raise ResolveError(
                    'Could not resolve environment or module: ' + path
                )

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

    raise ResolveError


def path_resolver(resolver, path):
    '''Resolves VirtualEnvironments with a relative or absolute path'''

    path = unipath(path)

    if is_environment(path):
        return VirtualEnvironment(path)

    raise ResolveError


def home_resolver(resolver, path):
    '''Resolves VirtualEnvironments in CPENV_HOME'''

    from .api import get_home_path

    path = unipath(get_home_path(), path)

    if is_environment(path):
        return VirtualEnvironment(path)

    raise ResolveError


def path_is_module_resolver(resolver, path):
    '''Checks if path is already a :class:`Module` object'''

    if isinstance(path, Module):
        return path

    raise ResolveError


def module_resolver(resolver, path):
    '''Resolves module in previously resolved environment.'''

    if resolver.resolved:

        if isinstance(resolver.resolved[0], VirtualEnvironment):
            env = resolver.resolved[0]
            mod = env.get_module(path)

            if mod:
                return mod

    raise ResolveError


def modules_path_resolver(resolver, path):
    '''Resolves modules in CPENV_MODULES path and CPENV_HOME/modules'''

    from .api import get_module_paths

    for module_dir in get_module_paths():
        mod_path = unipath(module_dir, path)

        if is_module(mod_path):
            return Module(mod_path)

    raise ResolveError


def active_env_module_resolver(resolver, path):
    '''Resolves modules in currently active environment.'''

    from .api import get_active_env

    env = get_active_env()
    if not env:
        raise ResolveError

    mod = env.get_module(path)
    if not mod:
        raise ResolveError

    return mod


def redirect_resolver(resolver, path):
    '''Resolves environment from .cpenv file...recursively walks up the tree
    in attempt to find a .cpenv file'''

    if not os.path.exists(path):
        raise ResolveError

    if os.path.isfile(path):
        path = os.path.dirname(path)

    for root, _, _ in walk_up(path):
        if is_redirecting(root):
            env_paths = redirect_to_env_paths(unipath(root, '.cpenv'))
            r = Resolver(*env_paths)
            return r.resolve()

    raise ResolveError


resolvers = [
    path_is_venv_resolver,
    path_resolver,
    home_resolver,
    redirect_resolver,
]

module_resolvers = [
    path_is_module_resolver,
    active_env_module_resolver,
    module_resolver,
    modules_path_resolver,
]
