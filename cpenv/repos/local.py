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

    def __init__(self, name, path):
        super(LocalRepo, self).__init__(name)
        self.path = utils.normpath(path)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.path == getattr(other, 'path', None) and
            self.name == other.name
        )

    def __hash__(self):
        return hash((self.__class__.__name__, self.path))

    def __repr__(self):
        return '<{}>(path="{}")'.format(self.__class__.__name__, self.path)

    def relative_path(self, *parts):
        return utils.normpath(self.path, *parts)

    def exact_match(self, module, string, name, version):
        return (
            module.qual_name == string or
            module.real_name == string or
            version and module.name == name and module.version == version or
            module.name == string
        )

    def partial_match(self, module, string, name, version):
        return module.name == name

    def find_module(self, matching):
        '''Return a single ModuleSpec.'''

        name, version = parse_module_path(
            matching,
            default_version=None,
        )

        matches = []
        for module in api.sort_modules(self.list_modules(), reverse=True):
            if self.exact_match(module, matching, name, version):
                return module
            if self.partial_match(module, matching, name, version):
                matches.append(module)

        # Choose the best match if no version was provided
        if not version and matches:
            return matches[0]

    def list_modules(self, matching=None):
        '''Return a list of ModuleSpec objects.

        Arguments:
            matching (str) - string used to filter modules
        '''

        if matching:
            name, version = parse_module_path(
                matching,
                default_version=None,
            )

        modules = []
        for module_file in glob(self.relative_path('*', 'module.yml')):
            module = Module(utils.normpath(os.path.dirname(module_file)))
            if (
                not matching or
                self.match_module(module, matching, name, version)
            ):
                modules.append(module)

        versions = glob(self.relative_path('*', '*', 'module.yml'))
        for version_file in versions:
            version_dir = os.path.dirname(version_file)
            module = Module(version_dir)
            if (
                not matching or
                self.match_module(module, matching, name, version)
            ):
                modules.append(module)

        return modules

    def clone_module(self, module, where, overwrite=False):
        '''Download a module using a ModuleSpec to the specified directory.'''

        if os.path.isdir(where):
            if not overwrite:
                raise OSError('%s already exists...' % where)
            else:
                utils.rmtree(where)

        shutil.copytree(module.path, where)

        return Module(where)

    def publish_module(self, module, overwrite=False):
        '''Upload a module'''

        if not overwrite and module.path.startswith(self.path):
            raise OSError(
                'Module already exists in repo...'
            )

        if module.version.string in module.real_name:
            new_module_path = self.relative_path(module.real_name)
        else:
            new_module_path = self.relative_path(
                module.name,
                module.version.string,
            )

        if os.path.isdir(new_module_path):
            if overwrite:
                utils.rmtree(new_module_path)
            else:
                raise OSError('Module already exists in repo...')

        shutil.copytree(module.path, new_module_path)
        return Module(new_module_path)

    def remove_module(self, module):
        '''Remove a module.'''

        if not module.path.startswith(self.path):
            raise OSError(
                'You can only remove modules from a repo that the module is '
                'actually in!'
            )

        module.remove()
