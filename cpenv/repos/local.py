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
from ..reporter import get_reporter
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

        src = module_spec.path
        dst = where

        reporter = get_reporter()
        progress_bar = reporter.progress_bar(
            label='Download %s' % module_spec.name,
            max_size=self.get_size(module_spec),
            data={'module_spec': module_spec},
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
            progress_bar.update(data={
                'module_spec': module_spec,
                'module': module,
            })

        return module

    def upload(self, module, overwrite=False):
        if not overwrite and module.path.startswith(self.path):
            raise OSError('Module already exists in repo...')

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

        src = module.path
        dst = new_module_path

        reporter = get_reporter()
        progress_bar = reporter.progress_bar(
            label='Upload %s' % module.name,
            max_size=self.get_size(module),
            data={'module': module, 'to_repo': self},
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

            module_spec = Module(new_module_path).as_spec()
            progress_bar.update(data={
                'module': module,
                'module_spec': module_spec,
            })

        return module_spec

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

    def get_size(self, module_spec):
        '''Sums the size of all files in the modules directory.'''

        if not os.path.isdir(module_spec.path):
            return -1

        return paths.get_folder_size(module_spec.path)

    def get_thumbnail(self, module_spec):
        '''Returns the path to a modules icon.png file'''

        if not os.path.isdir(module_spec.path):
            return

        icon_path = paths.normalize(module_spec.path, 'icon.png')
        if not os.path.isfile(icon_path):
            return

        return icon_path
