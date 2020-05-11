# -*- coding: utf-8 -*-
# Standard library imports
import os
import shutil
from glob import glob

# Local imports
from .. import paths
from ..module import (
    Module,
    is_exact_match,
    is_partial_match,
    sort_modules,
)
from ..vendor import yaml
from .base import Repo


class LocalRepo(Repo):
    '''Local Filesystem Repo.

    Supports two types of hierarchies.

    Flat:
        <repo_path>/<name>-<version>/module.yml

    Nested:
        <repo_path>/<name>/<version>/module.yml
    '''

    type_name = 'local'

    def __init__(self, name, path):
        super(LocalRepo, self).__init__(name)
        self.path = paths.normalize(path)
        self._cached_modules = None

    def relative_path(self, *parts):
        return paths.normalize(self.path, *parts)

    @property
    def cached_modules(self):
        if not self._cached_modules:
            self._cached_modules = sort_modules(
                self.list(),
                reverse=True
            )
        return self._cached_modules

    def find(self, requirement):
        matches = []
        for module_spec in self.cached_modules:
            if is_exact_match(requirement, module_spec):
                matches.insert(0, module_spec)
                continue
            if is_partial_match(requirement, module_spec):
                matches.append(module_spec)

        return matches

    def list(self):
        module_specs = []

        # Find flat module_specs
        for module_file in glob(self.relative_path('*', 'module.yml')):
            module_path = paths.normalize(os.path.dirname(module_file))
            module = Module(module_path, repo=self)
            module_specs.append(module.as_spec())

        # Find nested module_specs
        versions = glob(self.relative_path('*', '*', 'module.yml'))
        for version_file in versions:
            version_dir = paths.normalize(os.path.dirname(version_file))
            module = Module(version_dir, repo=self)
            module_specs.append(module.as_spec())

        return module_specs

    def download(self, module_spec, where, overwrite=False):
        if os.path.isdir(where):
            if not overwrite:
                raise OSError('%s already exists...' % where)
            else:
                paths.rmtree(where)

        shutil.copytree(module_spec.path, where)

        return Module(where)

    def upload(self, module, overwrite=False):
        if not overwrite and module.path.startswith(self.path):
            raise OSError(
                'Module already exists in repo...'
            )

        if module.version.string in module.real_name:
            # Use flat hierarchy when version already in module name
            new_module_path = self.relative_path(module.real_name)
        else:
            # Use nested hierarchy when version is not in module name
            new_module_path = self.relative_path(
                module.name,
                module.version.string,
            )

        if os.path.isdir(new_module_path):
            if overwrite:
                paths.rmtree(new_module_path)
            else:
                raise OSError('Module already exists in repo...')

        shutil.copytree(module.path, new_module_path)
        return Module(new_module_path)

    def remove(self, module_spec):
        '''Remove a module by module_spec.'''

        if module_spec.repo is not self:
            raise OSError(
                'You can only remove modules from a repo that the module is '
                'actually in!'
            )

        module = Module(module_spec.path)
        module.remove()

    def get_data(self, module_spec):
        '''Read a modules config data.'''

        if not os.path.isdir(module_spec.path):
            raise OSError('module_spec.path does not appare to exist.')

        module = Module(module_spec.path)
        return yaml.safe_load(module.raw_config)
