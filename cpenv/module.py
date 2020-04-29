# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import sys
from collections import namedtuple
from string import Template

# Local imports
from . import platform, utils, versions
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


ModuleSpec = namedtuple(
    'ModuleSpec',
    ['name', 'version', 'path', 'repo'],
)


class Module(object):

    def __init__(self, path, name=None, version=None):

        self.path = utils.normpath(path)

        # Create HookFinder for this module
        self.hook_path = self.relative_path('hooks')
        self.hook_finder = HookFinder(
            self.hook_path,
            get_global_hook_path(),
        )

        # Setup config
        self.config_path = self.relative_path('module.yml')
        self.config_vars = {
            'MODULE': self.path,
            'PLATFORM': platform,
            'PYVER': sys.version[:3],
        }
        self._raw_config = None
        self._config = None
        self._environ = None

        if name and version:

            # Use name and version if explicitly passed
            self.name = name
            self.version = versions.parse(version)

        else:

            # Check config
            if self.exists:
                name = self.config.get('name', None)
                version = self.config.get('version', None)

            # Last resort parse module path
            if name is None or version is None:
                name, version = parse_module_path(self.path)

            self.name = name
            self.version = version

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
        self.run_hook('pre_activate')
        api.add_active_module(self)
        self.run_hook('post_activate')

    def remove(self):
        from . import api
        self.run_hook('pre_remove')
        utils.rmtree(self.path)
        api.remove_active_module(self)
        self.run_hook('post_remove')

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
            self._raw_config = read_raw_config(self.config_path)

        return self._raw_config

    @property
    def config(self):
        if self._config is None:

            if not self.raw_config:
                self._config = {}
                return self._config

            self._config = read_config(self.config_path, self._raw_config)

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


def read_raw_config(module_file):

    with open(module_file, 'r') as f:
        return f.read()


def read_config(module_file, data=None):
    config_vars = {
        'MODULE': utils.normpath(os.path.dirname(module_file)),
        'PLATFORM': platform,
        'PYVER': sys.version[:3],
    }

    if data is None:
        with open(module_file, 'r') as f:
            data = f.read()

    return yaml.safe_load(Template(data).safe_substitute(config_vars))


def parse_module_path(path):
    '''Return name and version from a module's path.'''

    basename = os.path.basename(path)

    try:
        version = versions.parse(basename)
    except versions.ParseError:
        return basename, versions.default()

    head = basename.replace(version.string, '')
    if head:
        name = head.rstrip('_v').rstrip('-v').rstrip('-_')
    else:
        name = os.path.basename(os.path.dirname(path))

    return name, version


def is_module(path):
    '''Returns True if path refers to a module'''

    return os.path.exists(utils.normpath(path, 'module.yml'))
