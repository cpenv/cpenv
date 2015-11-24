# -*- coding: utf-8 -*-

import os
import shutil
import sys
from .utils import unipath
from .deps import Git, Pip
from . import utils, platform
from .packages import yaml


class VirtualEnvironment(object):

    def __init__(self, path):
        self.path = unipath(path)
        self.name = os.path.basename(self.path)
        self.modules_path = unipath(self.path, 'modules')
        self.config_path = unipath(self.path, 'environment.yml')
        self.pip = Pip(unipath(self.bin_path, 'pip'))
        self.git = Git(self.path)
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
        return '<VirtualEnvironment>({0})'.format(self.path)

    @property
    def config(self):
        if self._config is None:
            with open(self.config_path, 'r') as f:
                self._config = yaml.load(f.read())

        return self._config

    @property
    def environment(self):
        if self._environ is None:
            self._environ = utils.preprocess_dict(
                self.config['environment'],
                variables={
                    'CPENV_ENVIRON': self.path,
                    'CPENV_PLATFORM': platform,
                    'CPENV_PYVER': sys.version[:3],
                }
            )
        return self._environ

    @property
    def site_path(self):
        '''Path to environments site-packages'''

        if platform == 'win':
            return unipath(self.path, 'Lib', 'site-packages')

        py_ver = 'python{0}'.format(sys.version[:3])
        return unipath(self.path, 'lib', py_ver, 'site-packages')

    @property
    def bin_path(self):
        '''Path to environments bin'''

        if platform == 'win':
            return unipath(self.path, 'Scripts')

        return unipath(self.path, 'bin')

    def activate(self):
        pass

    def add_module(self, name, git_repo):
        return self.git.clone(git_repo, unipath(self.module_path, name))

    def rem_module(self, name):
        module_path = unipath(self.modules_path, name)
        if os.path.exists(module_path):
            shutil.rmtree(module_path)

    def get_module(self, name):
        module_path = unipath(self.modules_path, name)
        if os.path.exists(module_path):
            return Module(module_path)

    def get_modules(self):
        modules = []

        module_names = os.listdir(self.modules_path)
        for name in module_names:
            modules.append(Module(unipath(self.modules_path, name)))

        return modules


class Module(object):

    def __init__(self, path):
        self.path = unipath(path)
        self.name = os.path.basename(self.path)
        self.parent = VirtualEnvironment(unipath(self.path, '..', '..'))
        self.config_path = unipath(path, 'environment.yml')
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

    @property
    def config(self):
        if self._config is None:
            with open(self.config_path, 'r') as f:
                self._config = yaml.load(f.read())

        return self._config

    @property
    def environment(self):
        if self._environ is None:
            self._environ = utils.preprocess_dict(
                self.config['environment'],
                variables={
                    'CPENV_ENVIRON': self.parent.path,
                    'CPENV_MODULE': self.path,
                    'CPENV_PLATFORM': platform,
                    'CPENV_PYVER': sys.version[:3],
                }
            )

        return self._environ

    def activate(self):
        pass
