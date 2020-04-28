# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import sys
from string import Template

# Local imports
from . import platform, utils
from .hooks import HookFinder, get_global_hook_path
from .vendor import yaml


module_header = '''
# Variables
# $MODULE - path to this module
# $PLATFORM - path to platform
# $PYVER - path to python version

# Wrap variables in brackets when they are nested within a string. For example:
#     DO 'this${variable}isnested/' NOT 'this$variableisnested'

'''


def is_module(path):
    '''Returns True if path refers to a module'''

    return os.path.exists(utils.normpath(path, 'module.yml'))


class ModuleSpec(object):

    def __init__(self, name, version, path, repo):
        self.name = name
        self.version = version
        self.path = path
        self.repo = repo


class Module(object):

    def __init__(self, path, name=None, version=None):
        self.path = utils.normpath(path)
        self.name = name or os.path.basename(self.path)
        self.version = version
        self.hook_path = self.relative_path('hooks')
        self.hook_finder = HookFinder(
            self.hook_path,
            get_global_hook_path(),
        )
        self.config_path = self.relative_path('module.yml')
        self.config_vars = {
            'MODULE': self.path,
            'PLATFORM': platform,
            'PYVER': sys.version[:3],
        }
        self._raw_config = None
        self._config = None
        self._environ = None

    def __eq__(self, other):
        if hasattr(other, 'path'):
            return self.path == other.path
        else:
            return self.path == other

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return '<Module>({0})'.format(self.path)

    def relative_path(self, *args):
        return utils.normpath(self.path, *args)

    def run_hook(self, hook_name):
        hook = self.hook_finder(hook_name)
        if hook:
            hook.run(self)

    def activate(self):
        from . import api
        self.run_hook('preactivatemodule')
        api.add_active_module(self)
        self.run_hook('postactivatemodule')

    def remove(self):
        from . import api
        self.run_hook('preremovemodule')
        utils.rmtree(self.path)
        api.remove_active_module(self)
        self.run_hook('postremovemodule')

    @property
    def is_active(self):
        from . import api
        return self in api.get_active_modules()

    @property
    def exists(self):
        paths = (
            self.path,
            self.config_path,
        )
        return all([os.path.exists(path) for path in paths])

    @property
    def raw_config(self):
        if self._raw_config is None:

            with open(self.config_path, 'r') as f:
                self._raw_config = f.read()

        return self._raw_config

    @property
    def config(self):
        if self._config is None:

            if not self.raw_config:
                self._config = {}
                return self._config

            bare = Template(self.raw_config)
            formatted = bare.safe_substitute(self.config_vars)
            self._config = yaml.safe_load(formatted)

        return self._config

    @property
    def environment(self):
        if self._environ is None:
            env = self.config.get('environment', {})
            additional = {
                'CPENV_ACTIVE_MODULES': [self.path],
            }
            env = utils.join_dicts(additional, env)
            self._environ = utils.preprocess_dict(env)

        return self._environ
