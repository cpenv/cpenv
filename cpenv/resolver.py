# -*- coding: utf-8 -*-

# Standard library imports
import os
import shlex

# Local imports
from . import mappings, paths
from .module import Module, best_match, is_exact_match, is_module
from .reporter import get_reporter
from .repos import LocalRepo

__all__ = [
    "ResolveError",
    "Resolver",
    "Activator",
    "Copier",
    "Localizer",
    "module_resolvers",
    "is_redirecting",
    "redirect_to_modules",
    "parse_redirect",
]


class ResolveError(Exception):
    """Raised when a Resolver fairs to resolve a module or list of modules."""


class Resolver(object):
    """Responsible for resolving ModuleSpecs from requirement strings.

    Modules will be looked up sequentially in all registered Repos. By default
    this order is:
        1. LocalRepo pointing to current working directory
        2. LocalRepo pointing to cpenv_user_modules_path
        3. LocalRepo pointing to cpenv_home_modules_path ($CPENV_HOME/modules)
        4. LocalRepos pointing to the paths in $CPENV_MODULES
        5. Custom Repos registered via cpenv.add_repo

    If there are still unresolved modules, fallback to the old algorithm
    for module lookups using the resolve functions in the
    cpenv.resolver.module_resolvers list.
    """

    def __init__(self, repos):
        self.repos = repos
        self.reporter = get_reporter()

    def resolve(self, requirements):
        """Given a list of requirement strings, resolve ModuleSpecs.

        Returns:
            list of ModuleSpec objects

        Raises:
            ResolveError when a requirement can not be resolved.
        """

        self.reporter.start_resolve(requirements)
        unresolved = list(requirements)
        resolved = []

        # Try the old resolution alogirthm for backwards compatability
        resolved.extend(old_resolve_algorithm(self, unresolved))

        for requirement in list(unresolved):
            self.reporter.find_requirement(requirement)
            # TODO: handle more complex requirements.
            #       possibly use the new resolvelib being developed by pypa

            match_gen = (
                module_spec
                for repo in self.repos
                for module_spec in repo.find(requirement)
            )

            # best_match returns the first ModuleSpec that matches
            # both name and version or the ModuleSpec with the
            # highest version > the required version
            match = best_match(requirement, match_gen)
            if match:
                self.reporter.resolve_requirement(requirement, match)
                unresolved.remove(requirement)
                resolved.append(match)
            else:
                # TODO: once old resolve algorithm is removed
                # report a module resolution failure here.
                pass

        self.reporter.end_resolve(resolved, unresolved)

        if unresolved:
            raise ResolveError("Could not resolve: " + " ".join(unresolved))

        return resolved


class Activator(object):
    """Responsible for activating modules."""

    def __init__(self, localizer=None):
        self.localizer = localizer or Localizer(to_repo="home")

    def combine_modules(self, modules):
        """Combine a list of module's environments."""
        return mappings.join_dicts(*[obj.environment for obj in modules])

    def activate(self, module_specs):
        """Activate a list of module specs."""

        modules = self.localizer.localize(module_specs)
        env = self.combine_modules(modules)
        mappings.set_env(env)

        for module in modules:
            module.activate()

        return modules


class Copier(object):
    """Responsible for copying modules to a specific module."""

    def __init__(self, to_repo):
        from .api import get_repo

        self.to_repo = get_repo(to_repo)

    def copy(self, module_specs, overwrite=False):
        """Given ModuleSpecs, copy them to this copiers to_repo."""
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

            # Get local module or download module from repo
            if isinstance(module_spec.repo, LocalRepo):
                module = Module.from_spec(module_spec)
            else:
                download_path = get_cache_path(
                    "tmp",
                    str(hash(module_spec.repo.name)),
                    module_spec.name,
                    module_spec.version.string,
                )
                module = module_spec.repo.download(
                    module_spec,
                    where=download_path,
                    overwrite=overwrite,
                )

            # Upload module to_repo
            new_module_spec = self.to_repo.upload(
                module,
                overwrite=overwrite,
            )
            copied.append(new_module_spec)

        tmp = get_cache_path("tmp")
        if os.path.isdir(tmp):
            paths.rmtree(tmp)

        # Clear to_repo's cache as it doesn't include the localized modules
        self.to_repo.clear_cache()

        return copied


class Localizer(object):
    """Downloads modules from remote Repos to a specific LocalRepo.

    This is similar to a copy operation, but skips all module_specs that are
    already in LocalRepos. If they are in LocalRepos then they are already
    available to be activated.
    """

    def __init__(self, to_repo="home"):
        from .api import get_repo

        self.to_repo = get_repo(to_repo)
        self.reporter = get_reporter()

        if not isinstance(self.to_repo, LocalRepo):
            raise ValueError("Localizer expected LocalRepo got %s" % type(to_repo))

    def localize(self, module_specs, overwrite=False):
        """Given ModuleSpecs, download them to this Localizers repo."""

        self.reporter.start_localize(module_specs)
        localized = []
        for module_spec in module_specs:
            self.reporter.localize_module(module_spec, None)

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
                new_module_path = self.to_repo.relative_path(module_spec.real_name)
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

        self.reporter.end_localize(localized)

        # Clear to_repo's cache as it doesn't include the localized modules
        self.to_repo.clear_cache()

        return localized


def old_resolve_algorithm(resolver, paths):
    """Deprecated: Pre-0.5.0 resolution algorithm.

    Included for backwards compatability.
    """

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


def system_path_resolver(resolver, path):
    """Checks if path is already a :class:`Module` object"""

    is_system_path = "/" in path or "\\" in path or path.startswith(".")
    if is_system_path:
        mod_path = paths.normalize(path)
        if is_module(mod_path):
            resolved = Module(mod_path).to_spec()
            resolver.reporter.resolve_requirement(path, resolved)
            return resolved

    raise ResolveError


def redirect_resolver(resolver, path):
    """Resolves environment from .cpenv file...recursively walks up the tree
    in attempt to find a .cpenv file
    """

    if not os.path.exists(path):
        raise ResolveError

    if os.path.isfile(path):
        path = paths.parent(path)

    for root, _, _ in paths.walk_up(path):
        if is_redirecting(root):
            env_paths = redirect_to_modules(paths.normalize(root, ".cpenv"))
            r = Resolver(resolver.repos)
            return r.resolve(env_paths)

    raise ResolveError


module_resolvers = [
    redirect_resolver,
    system_path_resolver,
]


def is_redirecting(path):
    """Returns True if path contains a .cpenv file"""

    candidate = paths.normalize(path, ".cpenv")
    return os.path.exists(candidate) and os.path.isfile(candidate)


def redirect_to_modules(path):
    """Get environment path from redirect file"""

    with open(path, "r") as f:
        data = f.read()

    return parse_redirect(data)


def parse_redirect(data):
    """Parses a redirect string - data of a .cpenv file"""

    lines = [line for line in data.split("\n") if line.strip()]
    if len(lines) == 1:
        return shlex.split(lines[0])
    else:
        return lines
