# -*- coding: utf-8 -*-

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
        self.modules = None
        self.combined = None

    def resolve(self):
        '''Resolve all paths'''

        from . import api

        self.resolved = []
        paths = list(self.paths)

        # Attempt to resolve paths using Repos
        for path in list(paths):

            for repo in api.get_repos():

                module_or_spec = repo.find_module(path)
                if module_or_spec:
                    self.resolved.append(module_or_spec)
                    paths.remove(path)
                    break

        # Call the old resolution algorithm for backwards compatability
        self.resolved.extend(_old_resolve_algorithm(paths))

        # If we have left over paths we did not resolve everything!!
        if paths:
            raise ResolveError(
                'Could not resolve: ' + ' '.join(paths)
            )

        return self.resolved

    def localize(self):
        '''Localize all resolved modules.'''

        if self.resolved is None:
            raise ValueError('You must call Resolver.resolve first.')

        self.modules = []
        for module in self.resolved:
            if isinstance(module, Module):
                self.modules.append(module)
                continue

            # We hit a ModuleSpec - we need to localize it.
            module_spec = module
            repo = module.repo
            module = repo.localize_module(module_spec)
            self.modules.append(module)

    def combine(self):
        '''Combine all of the resolved modules environments.'''

        if self.modules is None:
            raise ValueError('You must call resolve and localize first.')

        return join_dicts(*[obj.environment for obj in self.modules])

    def activate(self):
        '''Active this resolvers resolved modules.'''

        if self.resolved is None:
            self.resolve()

        if self.modules is None:
            self.localize()

        # Combine and set environment variables
        set_env(self.combine())

        # Activate all modules
        for obj in self.modules:
            obj.activate()


def _old_resolve_algorithm(paths):
    '''Extracted and maintained for backwards compatability.'''

    modules = []
    for path in list(paths):

        for resolver in module_resolvers:
            try:

                resolved = resolver(path)
                paths.remove(path)

                if isinstance(resolved, Module):
                    modules.append(resolved)
                else:
                    modules.extend(resolved)

                break
            except ResolveError:
                continue

    return modules


def path_is_module_resolver(path):
    '''Checks if path is already a :class:`Module` object'''

    if isinstance(path, Module):
        return path

    raise ResolveError


def cwd_resolver(path):
    '''Checks if path is already a :class:`Module` object'''

    mod_path = normpath(os.getcwd(), path)
    if is_module(mod_path):
        return Module(mod_path)

    raise ResolveError


def modules_path_resolver(path):
    '''Resolves modules in CPENV_MODULES path and CPENV_HOME/modules'''

    from .api import get_module_paths

    for module_dir in get_module_paths():
        mod_path = normpath(module_dir, path)

        if is_module(mod_path):
            return Module(mod_path)

    raise ResolveError


def redirect_resolver(path):
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
