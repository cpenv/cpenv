# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import sys
from collections import namedtuple
from string import Template

# Local imports
from . import compat, mappings, paths
from .versions import ParseError, Version, default_version, parse_version
from .hooks import HookFinder, get_global_hook_path
from .vendor import yaml

__all__ = [
    'ModuleSpec',
    'Module',
    'sort_modules',
]
module_header = '''
# Variables
# $MODULE - path to this module
# $PLATFORM - platform name (win, mac, linux)
# $PYVER - python version (2.7, 3.6...)

# Wrap variables in brackets when they are nested within a string.
#     DO 'this${variable}isnested/' NOT 'this$variableisnested'

'''


ModuleSpec = namedtuple(
    'ModuleSpec',
    ['name', 'real_name', 'qual_name', 'version', 'path', 'repo'],
)


class Module(object):

    def __init__(self, path, name=None, version=None, repo=None):

        self.path = paths.normalize(path)
        self.repo = repo

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
            'PLATFORM': compat.platform,
            'PYVER': sys.version[:3],
        }
        self._raw_config = None
        self._config = None
        self._environ = None

        # Determine name, version, qual_name, and real_name

        if name and version:

            # Use name and version if explicitly passed
            self.name = name
            self.version = parse_version(version)

        else:

            # Check config
            if self.exists:
                name = self.config.get('name', None)
                version = self.config.get('version', None)
                if version:
                    version = parse_version(version)

            # Last resort parse module path
            if name is None or version is None:
                name, version = parse_module_path(self.path)

            self.name = name
            self.version = version

        self.qual_name = self.name + '-' + self.version.string

        base_name = os.path.basename(self.path)
        if self.version.string != base_name:
            self.real_name = base_name
        else:
            self.real_name = self.qual_name

    def __eq__(self, other):
        if hasattr(other, 'path'):
            return self.path == other.path
        else:
            return self.path == other

    def __hash__(self):
        return hash((self.__class__.__name__, self.path))

    def __repr__(self):
        return '<{}>(path="{}", name="{}", version={})'.format(
            self.__class__.__name__,
            self.path,
            self.name,
            self.version,
        )

    def as_spec(self):
        return ModuleSpec(
            name=self.name,
            real_name=self.real_name,
            qual_name=self.qual_name,
            version=self.version,
            path=self.path,
            repo=self.repo,
        )

    @classmethod
    def from_spec(cls, module_spec):
        return cls(
            name=module_spec.name,
            version=module_spec.version.string,
            path=module_spec.path,
            repo=module_spec.repo,
        )

    def relative_path(self, *args):
        '''Get a path relative to this module'''

        return paths.normalize(self.path, *args)

    def run_hook(self, hook_name):
        '''Run a module hook by name, fallback to global hook location.'''

        hook = self.hook_finder(hook_name)
        if hook:
            return hook.run(self)

    def spec(self, **kwargs):
        '''Return a ModuleSpec object for this Module.'''

        return ModuleSpec(
            name=kwargs.get('name', self.name),
            real_name=kwargs.get('real_name', self.real_name),
            qual_name=kwargs.get('qual_name', self.qual_name),
            path=kwargs.get('path', self.path),
            version=kwargs.get('version', self.version),
            repo=kwargs.get('repo', None),
        )

    def activate(self):
        '''Add this module to active modules'''

        from . import api
        self.run_hook('pre_activate')
        api.add_active_module(self)
        self.run_hook('post_activate')

    def remove(self):
        '''Delete this module'''

        from . import api
        self.run_hook('pre_remove')
        paths.rmtree(self.path)
        api.remove_active_module(self)
        self.run_hook('post_remove')

    @property
    def icon(self):
        return self.relative_path('icon.png')

    def has_icon(self):
        return os.path.isfile(self.icon)

    @property
    def description(self):
        return self.config.get('description', '')

    @property
    def author(self):
        return self.config.get('author', '')

    @property
    def email(self):
        return self.config.get('email', '')

    @property
    def is_active(self):
        from . import api
        return self.real_name in api.get_active_modules()

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

            self._config = read_config(
                self.config_path,
                self.config_vars,
                self._raw_config,
            )

        return self._config

    @property
    def environment(self):
        if self._environ is None:
            env = self.config.get('environment', {})
            additional = {
                'CPENV_ACTIVE_MODULES': [self.real_name],
            }
            env = mappings.join_dicts(additional, env)
            self._environ = mappings.preprocess_dict(env)

        return self._environ


def read_raw_config(module_file):
    ''''Read the raw text data of a module.yml file'''

    with open(module_file, 'r') as f:
        return f.read()


def read_config(module_file, config_vars=None, data=None):
    '''Read and formats a module.yml file'''

    if config_vars is None:
        config_vars = {
            'MODULE': paths.normalize(os.path.dirname(module_file)),
            'PLATFORM': compat.platform,
            'PYVER': sys.version[:3],
        }

    if data is None:
        with open(module_file, 'r') as f:
            data = f.read()

    return yaml.safe_load(Template(data).safe_substitute(config_vars))


def sort_modules(modules, reverse=False):
    '''Sort a list of Modules or ModuleSpecs by version.'''

    return sorted(
        modules,
        key=lambda m: (m.real_name, m.version),
        reverse=reverse
    )


def is_module(path):
    '''Returns True if path refers to a module'''

    return os.path.exists(paths.normalize(path, 'module.yml'))


def parse_module_path(path, default_version=default_version):
    '''Return name and version from a module's path.'''

    basename = os.path.basename(path)

    try:
        version = parse_version(basename)
    except ParseError:
        if callable(default_version):
            default = default_version()
        else:
            default = default_version
        return basename, default

    head = basename.replace(version.string, '')
    if head:
        name = head.rstrip('_v').rstrip('-v').rstrip('-_')
    else:
        name = os.path.basename(os.path.dirname(path))

    return name, version


def parse_module_requirement(requirement, default_version=None):
    '''Given a requirement, return a name and version.'''

    if '\\' in requirement or '/' in requirement:
        # Probably a system path - lets parse it.
        return parse_module_path(requirement, default_version=default_version)

    try:
        version = parse_version(requirement)
    except ParseError:
        if callable(default_version):
            default = default_version()
        else:
            default = default_version
        return requirement, default

    name = requirement
    head = requirement.replace(version.string, '')
    if head:
        name = head.rstrip('_v').rstrip('-v').rstrip('-_').rstrip('<>=!')

    return name, version


def is_exact_match(requirement, module_spec):
    '''Is the module_spec an exact match for the provided requirement?'''

    name, version = parse_module_requirement(requirement)
    return (
        module_spec.qual_name == requirement or
        module_spec.real_name == requirement or
        (
            version and module_spec.name == name and
            module_spec.version == version
        )
    )


def is_partial_match(requirement, module_spec):
    '''Is the module_spec a partial match for the provided requirement?'''

    name, version = parse_module_requirement(requirement)
    return module_spec.name == name


def best_match(requirement, module_specs):

    name, version = parse_module_requirement(
        requirement,
        Version(0, 0, 0, None, None, '*')
    )

    best_match = None
    for module_spec in module_specs:
        if is_exact_match(requirement, module_spec):
            return module_spec
        if version < module_spec.version:
            if not best_match:
                best_match = module_spec
                continue
            if best_match.version < module_spec.version:
                best_match = module_spec

    return best_match
