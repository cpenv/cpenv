# -*- coding: utf-8 -*-
# Standard library imports
import os
import shutil
from glob import glob

# Local imports
from .. import api, utils
from ..module import Module, ModuleSpec, parse_module_path
from .base import Repo


class LocalRepo(Repo):
    '''Local Filesystem Repo.

    Find's modules in a filesystem directory. Supports a flat and nested
    hierarchy.

    A flat hierarchy is like:
        <repo_path>/<name>-<version>/module.yml

    A nested hierarchy is like:
        <repo_path>/<name>/<version>/module.yml
    '''

    def __init__(self, path):
        self.path = utils.normpath(path)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.path == getattr(other, 'path', None)
        )

    def __hash__(self):
        return hash((self.__class__.__name__, self.path))

    def __repr__(self):
        return '<{}>(path="{}")'.format(self.__class__.__name__, self.path)

    def relative_path(self, *parts):
        return utils.normpath(self.path, *parts)

    def match_module(self, module, requirement, name, version):
        return (
            module.qual_name == requirement or
            module.real_name == requirement or
            version and module.name == name and module.version == version or
            module.name == name
        )

    def find_module(self, requirement):
        '''Return a single ModuleSpec object matching the requirement.'''

        name, version = parse_module_path(
            requirement,
            default_version=None,
        )

        for module in api.sort_modules(self.list_modules(), reverse=True):
            if self.match_module(module, requirement, name, version):
                return module

    def list_modules(self, requirement=None):
        '''Return a list of ModuleSpec objects matching the requirement.

        If no requirement is provided, list all ModuleSpecs available in the
        repo.
        '''

        if requirement:
            name, version = parse_module_path(
                requirement,
                default_version=None,
            )

        modules = []
        for module_file in glob(self.relative_path('*', 'module.yml')):
            module = Module(utils.normpath(os.path.dirname(module_file)))
            if not requirement or self.match_module(module, requirement, name):
                modules.append(module)

        versions = glob(self.relative_path('*', '*', 'module.yml'))
        for version_file in versions:
            version_dir = os.path.dirname(version_file)
            module = Module(version_dir)
            if not requirement or self.match_module(module, requirement, name):
                modules.append(module)

        return modules

    def clone_module(self, module, where, overwrite=True):
        '''Download a module using a ModuleSpec to the specified directory.'''

        if os.path.isdir(where):
            if not overwrite:
                raise OSError('%s already exists...' % where)
            else:
                utils.rmtree(where)

        shutil.copytree(module.path, where)

        return Module(where)

    def publish_module(self, module):
        '''Upload a module'''

        if module.path.startswith(self.path):
            raise OSError(
                'Can not upload_module that is already in LocalRepo...'
            )

        name = module.config.get('name', module.name)
        version = module.config.get('version', module.version)
        new_module_path = self.relative_path(name)
        if version and name.endswith(version):
            basename = name.replace(version, '').rstrip('-_')
            if basename[-2:] in ['-v', '_v']:
                basename = basename[:-2]
            new_module_path = self.relative_path(basename, version)

        if os.path.isdir(new_module_path):
            raise OSError('Module already exists in repo...')

        shutil.copytree(module.path, new_module_path)
        return Module(new_module_path)
