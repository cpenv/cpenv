# -*- coding: utf-8 -*-

# Standard library imports
import os

# Local imports
from . import utils
from .repos import LocalRepo
from .module import Module, is_module, is_exact_match, best_match


class ResolveError(Exception):
    '''Raised when a Resolver fairs to resolve a module or list of modules.'''


class Resolver(object):
    '''Responsible for resolving ModuleSpecs from requirement strings.

    Modules will be looked up sequentially in all registered Repos. By default
    this order is:
        1. LocalRepo pointing to current working directory
        2. LocalRepo pointing to cpenv_home_modules_path ($CPENV_HOME/modules)
        3. LocalRepo pointing to cpenv_user_modules_path
        4. LocalRepos pointing to the paths in $CPENV_MODULES
        5. Custom Repos registered via cpenv.add_repo

    If there are still unresolved modules, we fallback to the old algorithm
    for module lookups using the resolve functions in the
    cpenv.resolver.module_resolvers list.
    '''

    def __init__(self, repos):
        self.repos = repos

    def resolve(self, requirements):
        '''Given a list of requirement strings, resolve ModuleSpecs.

        Returns:
            list of ModuleSpec objects

        Raises:
            ResolveError when a requirement can not be resolved.
        '''

        unresolved = list(requirements)
        resolved = []

        for requirement in requirements:

            # TODO: handle more complex requirements.
            #       possibly use the new resolvelib being developed by pypa

            match_gen = (
                module_spec for repo in self.repos
                for module_spec in repo.find(requirement)
            )

            # best_match returns the first ModuleSpec that matches
            # both name and version or the ModuleSpec with the
            # highest version > the requirement
            match = best_match(requirement, match_gen)
            if match:
                unresolved.remove(requirement)
                resolved.append(match)

        if unresolved:
            # Try the old resolution alogirthm for backwards compatability
            resolved.extend(old_resolve_algorithm(self, unresolved))

        if unresolved:
            raise ResolveError(
                'Could not resolve: ' + ' '.join(unresolved)
            )

        return resolved


class Activator(object):
    '''Responsible for activating modules.'''

    def __init__(self, localizer=None):
        self.localizer = localizer or Localizer(to_repo='home')

    def combine_modules(self, modules):
        '''Combine a list of module's environments.'''

        return utils.join_dicts(*[obj.environment for obj in modules])

    def activate(self, module_specs):
        '''Activate a list of module specs.'''

        modules = self.localizer.localize(module_specs)
        env = self.combine_modules(modules)
        utils.set_env(env)

        for module in modules:
            module.activate()

        return modules


class Copier(object):
    '''Responsible for copying modules to a specific module.'''

    def __init__(self, to_repo):
        from .api import get_repo
        self.to_repo = get_repo(to_repo)

    def copy(self, module_specs, overwrite=False):
        '''Given ModuleSpecs, copy them to this copiers to_repo.'''
        from .api import get_cache_path

        copied = []
        for module_spec in module_specs:

            matches = self.to_repo.find(module_spec.qual_name)
            already_exists = False
            for match in matches:
                if is_exact_match(module_spec.qual_name, match):
                    already_exists = True
                    break

            if already_exists and not overwrite:
                continue

            # Generate a new module path in to_repo
            download_path = get_cache_path(
                'temp_downloads',
                str(hash(module_spec.repo.name)),
                module_spec.name,
                module_spec.version.string,
            )
            module = module_spec.repo.download(
                module_spec,
                where=download_path,
                overwrite=overwrite,
            )
            new_module_spec = self.to_repo.upload(
                module,
                overwrite=overwrite
            )
            copied.append(new_module_spec)

        temp_downloads = get_cache_path('temp_downloads')
        if os.path.isdir(temp_downloads):
            utils.rmtree(temp_downloads)

        return copied


class Localizer(object):
    '''Downloads modules from remote Repos to a specific LocalRepo.

    This is similar to a copy operation, but skips all module_specs that are
    already in LocalRepos. If they are in LocalRepos then they are already
    available to be activated.
    '''

    def __init__(self, to_repo='home'):
        from .api import get_repo

        self.to_repo = get_repo(to_repo)

        if not isinstance(self.to_repo, LocalRepo):
            raise ValueError(
                'Localizer expected LocalRepo got %s' % type(to_repo)
            )

    def localize(self, module_specs, overwrite=False):
        '''Given ModuleSpecs, download them to this Localizers repo.'''

        localized = []
        for module_spec in module_specs:

            # Module is already local
            if isinstance(module_spec.repo, LocalRepo):
                localized.append(Module(module_spec.path))
                continue

            # Module already exists in to_repo
            matches = self.to_repo.find(module_spec.qual_name)
            already_exists = False
            for match in matches:
                if is_exact_match(module_spec.qual_name, match):
                    already_exists = True
                    localized.append(Module(match.path))
                    break

            if already_exists and not overwrite:
                continue

            # Generate a new module path in to_repo
            if module_spec.version.string in module_spec.real_name:
                new_module_path = self.to_repo.relative_path(
                    module_spec.real_name
                )
            else:
                new_module_path = self.to_repo.relative_path(
                    module_spec.name,
                    module_spec.version.string,
                )

            module = module_spec.repo.download(
                module_spec,
                where=new_module_path,
                overwrite=overwrite,
            )
            localized.append(module)

        return localized


# Deprecated!!
# The following functions represet the old resolution algorithm
# this is called by Resolver.resolve only when no Repos are able to resolve
# a requirement.

def old_resolve_algorithm(resolver, paths):

    modules = []
    for path in list(paths):

        for module_resolver in module_resolvers:
            try:

                resolved = module_resolver(resolver, path)
                paths.remove(path)

                if isinstance(resolved, list):
                    modules.extend(resolved)
                else:
                    modules.append(resolved)

                break
            except ResolveError:
                continue

    return modules


def path_is_module_resolver(resolver, path):
    '''Checks if path is already a :class:`Module` object'''

    if isinstance(path, Module):
        return path

    raise ResolveError


def cwd_resolver(resolver, path):
    '''Checks if path is already a :class:`Module` object'''

    mod_path = utils.normpath(os.getcwd(), path)
    if is_module(mod_path):
        return Module(mod_path).as_spec()

    raise ResolveError


def modules_path_resolver(resolver, path):
    '''Resolves modules in CPENV_MODULES path and CPENV_HOME/modules'''

    from .api import get_module_paths

    for module_dir in get_module_paths():
        mod_path = utils.normpath(module_dir, path)

        if is_module(mod_path):
            return Module(mod_path).as_spec()

    raise ResolveError


def redirect_resolver(resolver, path):
    '''Resolves environment from .cpenv file...recursively walks up the tree
    in attempt to find a .cpenv file'''

    if not os.path.exists(path):
        raise ResolveError

    if os.path.isfile(path):
        path = os.path.dirname(path)

    for root, _, _ in utils.walk_up(path):
        if utils.is_redirecting(root):
            env_paths = utils.redirect_to_modules(
                utils.normpath(root, '.cpenv')
            )
            r = Resolver(resolver.repos)
            return r.resolve(env_paths)

    raise ResolveError


module_resolvers = [
    redirect_resolver,
    cwd_resolver,
    path_is_module_resolver,
    modules_path_resolver,
]
