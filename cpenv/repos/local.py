# -*- coding: utf-8 -*-
# Standard library imports
import glob
import os
import shutil

# Local imports
from .. import utils
from ..module import Module, ModuleSpec
from .base import Repo


class LocalRepo(Repo):
    '''Local Filesystem Repo.

    Find's modules in a filesystem directory. Supports a flat and nested
    hierarchy.

    A flat hierarchy is like:
        <repo_path>/<module_name>/module.yml

    A nested hierarchy is like:
        <repo_path>/<module_name>/<version>/module.yml
    '''

    def __init__(self, path):
        self.path = path

    def _relpath(self, *parts):
        return utils.normpath(self.path, *parts)

    def _make_spec(self, module):
        return ModuleSpec(
            name=module.config.get('name', module.name),
            version=module.config.get('version', module.version),
            path=module.path,
            repo=self,
        )

    def find_module(self, requirement):
        '''Return a single ModuleSpec object matching the requirement.'''

        candidate = self._relpath(requirement)
        candidate_file = self._relpath(requirement, 'module.yml')
        if os.path.isfile(candidate_file):
            return self._make_spec(Module(candidate))

        versions = glob.glob(self._relpath(requirement, '*', 'module.yml'))
        if versions:
            latest = utils.normpath(sorted(versions)[-1])
            latest_dir = os.path.dirname(latest)
            version = os.path.basename(latest_dir)
            name = os.path.basename(os.path.dirname(latest_dir))
            module = Module(latest_dir, name=name, version=version)
            return self._make_spec(module)

    def list_modules(self):
        '''Return a list of ModuleSpec objects matching the requirement.

        If no requirement is provided, list all ModuleSpecs available in the
        repo.
        '''

        modules = []
        for module_file in glob.glob(self._relpath('*', 'module.yml')):
            module = Module(utils.normpath(os.path.dirname(module_file)))
            modules.append(self._make_spec(module))

        versions = glob.glob(self._relpath('*', '*', 'module.yml'))
        for version_file in versions:
            version_dir = os.path.dirname(version_file)
            version = os.path.basename(version_dir)
            name = os.path.basename(os.path.dirname(version_dir))
            module = Module(version_dir, name=name, version=version)
            modules.append(self._make_spec(module))

        return modules

    def download_module(self, spec, where, overwrite=True):
        '''Download a module using a ModuleSpec to the specified directory.'''

        if os.path.isdir(where):
            if not overwrite:
                raise OSError('%s already exists...' % where)
            else:
                utils.rmtree(where)

        shutil.copytree(spec.path, where)

        return Module(where)

    def upload_module(self, module):
        '''Upload a module'''

        if module.path.startswith(self.path):
            raise OSError(
                'Can not upload_module that is already in LocalRepo...'
            )

        name = module.config.get('name', module.name)
        version = module.config.get('version', module.version)
        new_module_path = self._relpath(name)
        if version and name.endswith(version):
            basename = name.replace(version, '').rstrip('-_')
            if basename[-2:] in ['-v', '_v']:
                basename = basename[:-2]
            new_module_path = self._relpath(basename, version)

        if os.path.isdir(new_module_path):
            raise OSError('Module already exists in repo...')

        shutil.copytree(module.path, new_module_path)
        return Module(new_module_path)
