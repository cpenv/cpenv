# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os

# Local imports
from .module import Module, is_module
from .utils import (
    is_redirecting,
    join_dicts,
    normpath,
    redirect_to_modules,
    set_env,
    walk_up,
)


'''
cpenv.resolver
==============
Defines :class:`Resolver` used to resolve cpenv :class:`Module` s.
'''


class ResolveError(Exception):
    pass


class Resolver(object):
    '''Resolve, combine, and activate :class:`Module`s.

    Modules will be looked up using the resolver functions in the
    cpenv.resolver.module_resolvers list.

    usage::

        >>> Resolver('module_a', 'module_b', 'module_c')
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


def path_is_module_resolver(resolver, path):
    '''Checks if path is already a :class:`Module` object'''

    if isinstance(path, Module):
        return path

    raise ResolveError


def cwd_resolver(resolver, path):
    '''Checks if path is already a :class:`Module` object'''

    mod_path = normpath(os.getcwd(), path)
    if is_module(mod_path):
        return Module(mod_path)

    raise ResolveError


def modules_path_resolver(resolver, path):
    '''Resolves modules in CPENV_MODULES path and CPENV_HOME/modules'''

    from .api import get_module_paths

    for module_dir in get_module_paths():
        mod_path = normpath(module_dir, path)

        if is_module(mod_path):
            return Module(mod_path)

    raise ResolveError


def redirect_resolver(resolver, path):
    '''Resolves environment from .cpenv file...recursively walks up the tree
    in attempt to find a .cpenv file'''

    if not os.path.exists(path):
        raise ResolveError

    if os.path.isfile(path):
        path = os.path.dirname(path)

    for root, _, _ in walk_up(path):
        if is_redirecting(root):
            env_paths = redirect_to_modules(normpath(root, '.cpenv'))
            r = Resolver(*env_paths)
            return r.resolve()

    raise ResolveError


module_resolvers = [
    redirect_resolver,
    cwd_resolver,
    path_is_module_resolver,
    modules_path_resolver,
]
