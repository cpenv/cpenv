# -*- coding: utf-8 -*-

# Standard library imports
import logging
import os
import shutil
from fnmatch import fnmatch
from functools import partial
from glob import glob

# Local imports
from .. import compat, paths
from ..environment import Environment
from ..module import Module, is_exact_match, is_partial_match, sort_modules
from ..reporter import get_reporter
from ..vendor import yaml
from ..vendor.cachetools import TTLCache, cachedmethod, keys
from .base import Repo

_log = logging.getLogger(__name__)


class LocalRepo(Repo):
    """Local Filesystem Repo.

    Supports two types of hierarchies.

    Flat:
        <repo_path>/<name>-<version>/module.yml

    Nested:
        <repo_path>/<name>/<version>/module.yml

    Arguments:
        name (str): Name of the repository.
        path (str): Path to repository folder.
        priority (int): Sort order of repositories. Lower priority repositories take
            precedence over higher priority. Defaults to 10.
        nested (bool): When True the Repository will use the Nested hierarchy. Defaults
            to False.
    """

    type_name = "local"
    priority = 10

    def __init__(self, name, path, priority=None, nested=None):
        super(LocalRepo, self).__init__(name, priority)
        self.path = paths.normalize(path)
        self.cache = TTLCache(maxsize=10, ttl=60)

        self.nested = nested
        if nested is None:
            self.nested = bool(os.getenv("CPENV_LOCALREPO_NESTED", False))

    def relative_path(self, *parts):
        return paths.normalize(self.path, *parts)

    def clear_cache(self):
        self.cache.clear()

    @cachedmethod(lambda self: self.cache, key=partial(keys.hashkey, "find"))
    def find(self, requirement):
        matches = []
        for module_spec in self.list():
            if is_exact_match(requirement, module_spec):
                matches.insert(0, module_spec)
                continue
            if is_partial_match(requirement, module_spec):
                matches.append(module_spec)

        return matches

    @cachedmethod(lambda self: self.cache, key=partial(keys.hashkey, "list"))
    def list(self):
        module_specs = []

        # Find flat module_specs
        for module_file in glob(self.relative_path("*", "module.yml")):
            module_path = paths.parent(module_file)
            module = Module(module_path, repo=self)
            module_specs.append(module.to_spec())

        # Find nested module_specs
        versions = glob(self.relative_path("*", "*", "module.yml"))
        for version_file in versions:
            version_dir = paths.parent(version_file)
            module = Module(version_dir, repo=self)
            module_specs.append(module.to_spec())

        return sort_modules(module_specs, reverse=True)

    def download(self, module_spec, where, overwrite=False):
        if os.path.isdir(where):
            if not overwrite:
                raise OSError("%s already exists..." % where)
            else:
                paths.rmtree(where)

        src = module_spec.path
        dst = where

        reporter = get_reporter()
        progress_bar = reporter.progress_bar(
            label="Download %s" % module_spec.name,
            max_size=self.get_size(module_spec),
            data={"module_spec": module_spec},
        )
        with progress_bar as progress_bar:
            for root, _, files in paths.exclusive_walk(src):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, src)
                    dst_path = os.path.join(dst, rel_path)

                    if os.path.islink(src_path):
                        continue

                    dst_dir = os.path.dirname(dst_path)
                    if not os.path.isdir(dst_dir):
                        os.makedirs(dst_dir)

                    shutil.copy2(src_path, dst_path)
                    progress_bar.update(os.path.getsize(src_path))

            module = Module(where)
            progress_bar.update(
                data={
                    "module_spec": module_spec,
                    "module": module,
                }
            )

        return module

    def upload(self, module, overwrite=False):
        if not overwrite and module.path.startswith(self.path):
            raise OSError("Module already exists in repo...")

        # Generate a new module path in to_repo
        if self.nested:
            new_module_path = self.relative_path(
                module.name,
                module.version.string,
            )
        else:
            new_module_path = self.relative_path(module.qual_name)

        if os.path.isdir(new_module_path):
            if overwrite:
                paths.rmtree(new_module_path)
            else:
                raise OSError("Module already exists in repo...")

        src = module.path
        dst = new_module_path

        reporter = get_reporter()
        progress_bar = reporter.progress_bar(
            label="Upload %s" % module.name,
            max_size=self.get_size(module),
            data={"module": module, "to_repo": self},
        )
        with progress_bar as progress_bar:
            for root, _, files in paths.exclusive_walk(src):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, src)
                    dst_path = os.path.join(dst, rel_path)

                    if os.path.islink(src_path):
                        continue

                    dst_dir = os.path.dirname(dst_path)
                    if not os.path.isdir(dst_dir):
                        os.makedirs(dst_dir)

                    shutil.copy2(src_path, dst_path)
                    progress_bar.update(os.path.getsize(src_path))

            module_spec = Module(new_module_path).to_spec()
            progress_bar.update(
                data={
                    "module": module,
                    "module_spec": module_spec,
                }
            )

        return module_spec

    def remove(self, module_spec):
        """Remove a module by module_spec."""

        if module_spec.repo is not self:
            raise OSError(
                "You can only remove modules from a repo "
                "that the module is actually in!"
            )

        module = Module(module_spec.path)
        module.remove()

    def get_data(self, module_spec):
        """Read a modules config data."""

        if not os.path.isdir(module_spec.path):
            raise OSError("module_spec.path does not appear to exist.")

        module = Module(module_spec.path)
        return yaml.safe_load(module.raw_config)

    def get_size(self, module_spec):
        """Sums the size of all files in the modules directory."""

        if not os.path.isdir(module_spec.path):
            return -1

        return paths.get_folder_size(module_spec.path)

    def get_thumbnail(self, module_spec):
        """Returns the path to a modules icon.png file"""

        if not os.path.isdir(module_spec.path):
            return

        icon_path = paths.normalize(module_spec.path, "icon.png")
        if not os.path.isfile(icon_path):
            return

        return icon_path

    def validate_filters(self, filters):
        errors = {}
        name = filters.get("name")
        if name and not isinstance(name, compat.string_types):
            errors["name"] = "Name must be a string."

        requires = filters.get("requires")
        requires_error = "requires must be a list of strings."
        if requires:
            if not isinstance(requires, list):
                errors["requires"] = requires_error
            else:
                for require in requires:
                    if not isinstance(require, compat.string_types):
                        errors["requires"] = requires_error

        return not bool(errors), errors

    def list_environments(self, filters=None):
        """Returns a list of environments matching the provided filters."""

        if filters:
            valid, errors = self.validate_filters(filters)
            if not valid:
                _log.debug(
                    "Provided filters are incompatible with LocalRepo.\n"
                    "The following errors were found: %s",
                    errors,
                )

        filters = {}
        name_filter = filters.get("name", None)
        requires_filter = filters.get("requires", None)

        environments = []
        for file in glob(self.relative_path("..", "environments", "*.yml")):

            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f.read())

                env = Environment(
                    name=data.get("name", os.path.basename(file).rsplit(".", 1)[0]),
                    data=data,
                    path=paths.normalize(file),
                )

                # Check filters
                if name_filter and not fnmatch(env.name, name_filter):
                    continue

                if requires_filter:
                    if not set(requires_filter) - set(env["requires"]):
                        continue

                environments.append(env)

            except Exception as e:
                _log.error("Invalid Environment file: " + file)
                print(str(e))

        return environments

    def save_environment(self, name, data, force=False):
        """Saves an Environment to a yml file in the LocalRepo."""

        file = self.relative_path("..", "environments", name + ".yml")
        if not force and os.path.isfile(file):
            raise ValueError('Environment "%s" because it already exists.' % name)

        encoded = yaml.safe_dump(data)
        with open(file, "w") as f:
            f.write(encoded)

        return True

    def remove_environment(self, name):
        """Removes an Environment from the LocalRepo."""

        file = self.relative_path("..", "environments", name + ".yml")
        if os.path.isfile(file):
            os.remove(file)


class RemoteRepo(LocalRepo):
    """This Repository is identical to the LocalRepo but can be used to represent
    network locations. The idea being that in some cases you may want to localize
    packages from a network share to a truly local path like your CPENV_HOME.

    By configuring a RemoteRepo, modules can be stored on a network shared, but
    will be localized before being activated.
    """

    type_name = "remote"
    priority = 15
