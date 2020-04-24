# -*- coding: utf-8 -*-
'''
cpenv.models
============
Provides models for manipulating cpenv :class:`VirtualEnvironment` s and :class:`Module` s
'''

import os
import site
import shutil
import sys
import subprocess
from string import Template
from .vendor import yaml
from . import utils, platform
from .deps import Pip, Git
from .hooks import HookFinder, get_global_hook_path
from .log import logger
from .utils import unipath


class BaseEnvironment(object):
    '''Common baseclass for :class:`VirtualEnvironment` and :class:`Module`'''

    def __init__(self, path):
        self.path = unipath(path)
        self.name = os.path.basename(self.path)
        self.config_path = self.relative_path('environment.yml')
        self.hook_path = self.relative_path('hooks')
        self._config = None
        self._environ = None

        # These members must be defined in subclasses
        self.pip = None
        self.hook_finder = None
        self.git = None
        self.modules_path = None

    def __eq__(self, other):
        if hasattr(other, 'path'):
            return self.path == other.path
        else:
            return self.path == other

    def __hash__(self):
        return hash(self.path)

    @property
    def hook_args(self):
        raise NotImplementedError()

    def run_hook(self, hook_name):
        hook = self.hook_finder(hook_name)
        if hook:
            hook.run(*self.hook_args)

    def relative_path(self, *args):
        return unipath(self.path, *args)

    @property
    def exists(self):
        paths = (
            self.path,
            self.config_path,
        )

        return all([os.path.exists(path) for path in paths])

    @property
    def bare_config(self):
        with open(self.config_path, 'r') as f:
            config = f.read()

        return config

    @property
    def config(self):
        if self._config is None:

            if not self.bare_config:
                self._config = {}
                return self._config

            bare = Template(self.bare_config)
            formatted = bare.safe_substitute(self.variables)
            self._config = yaml.safe_load(formatted)

        return self._config

    @property
    def variables(self):
        raise NotImplementedError()

    @property
    def environment(self):
        if self._environ is None:
            env = self.config.get('environment', {})
            if env:
                self._environ = utils.preprocess_dict(env)
        return self._environ

    def activate(self):
        raise NotImplementedError()

    def remove(self):
        raise NotImplementedError()

    def update(self, updated=None):

        updated = updated or set()

        dependencies = self.config.get('dependencies', {})
        pip_installs = dependencies.get('pip', [])
        git_clones = dependencies.get('git', [])
        modules = dependencies.get('modules', [])

        for package in pip_installs:
            if package in updated:
                continue

            self.pip.upgrade(package)
            updated.add(package)

        for repo in git_clones:
            destination = unipath(self.path, repo['path'])
            if destination in updated:
                continue

            if not os.path.exists(destination):
                self.git.clone(
                    repo['repo'],
                    repo['path'],
                    repo.get('branch', None)
                )
            else:
                self.git.pull(destination)
            updated.add(destination)

        for repo in modules:
            if repo['name'] in updated:
                continue

            if repo['name'] not in os.listdir(self.modules_path):
                module = self.add_module(
                    repo['name'],
                    repo['repo'],
                    repo['branch'])
            else:
                module = self.get_module(repo['name'])

            module_updates = module.update(updated)
            updated.add(repo['name'])
            updated.update(module_updates)

        return updated


class VirtualEnvironment(BaseEnvironment):

    def __init__(self, path):
        super(VirtualEnvironment, self).__init__(path)

        self.config_path = self.relative_path('environment.yml')
        self.modules_path = self.relative_path('modules')
        self.hook_finder = HookFinder(self.hook_path, get_global_hook_path())
        self.pip = Pip(unipath(self.bin_path, 'pip'))
        self.git = Git(self.path)

    def __repr__(self):
        return '<VirtualEnvironment>({0})'.format(self.path)

    @property
    def hook_args(self):
        return self,

    @property
    def variables(self):
        return {
            'ENVIRON': self.path,
            'PLATFORM': platform,
            'PYVER': sys.version[:3],
        }

    @property
    def environment(self):
        if self._environ is None:
            env = self.config.get('environment', {})
            additional = {
                'PATH': [self.bin_path],
                'PYTHONPATH': [self.site_path],
                'CPENV_ACTIVE': [self.path],
            }
            env = utils.join_dicts(additional, env)
            self._environ = utils.preprocess_dict(env)

        return self._environ

    @property
    def is_active(self):
        return os.environ.get('CPENV_ACTIVE', '') == self.path

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

    def _pre_activate(self):
        '''
        Prior to activating, store everything necessary to deactivate this
        environment.
        '''

        if 'CPENV_CLEAN_ENV' not in os.environ:
            if platform == 'win':
                os.environ['PROMPT'] = '$P$G'
            else:
                os.environ['PS1'] = '\\u@\\h:\\w\\$'
            clean_env_path = utils.get_store_env_tmp()
            os.environ['CPENV_CLEAN_ENV'] = clean_env_path
            utils.store_env(path=clean_env_path)
        else:
            utils.restore_env_from_file(os.environ['CPENV_CLEAN_ENV'])

    def _activate(self):
        '''
        Do some serious mangling to the current python environment...
        This is necessary to activate an environment via python.
        '''

        old_syspath = set(sys.path)
        site.addsitedir(self.site_path)
        site.addsitedir(self.bin_path)
        new_syspaths = set(sys.path) - old_syspath
        for path in new_syspaths:
            sys.path.remove(path)
            sys.path.insert(1, path)

        if not hasattr(sys, 'real_prefix'):
            sys.real_prefix = sys.prefix

        sys.prefix = self.path

    def activate(self):
        self._pre_activate()
        self.run_hook('preactivate')
        self._activate()
        self.run_hook('postactivate')

    def remove(self):
        '''
        Remove this environment
        '''
        self.run_hook('preremove')
        utils.rmtree(self.path)
        self.run_hook('postremove')

    def update(self, updated=None):
        self.run_hook('preupdate')
        self.pip.install('cpenv')
        updated = super(VirtualEnvironment, self).update(updated)
        self.run_hook('postupdate')
        return updated

    def add_module(self, name, path, git_branch=None):
        module = Module(unipath(self.modules_path, name))
        if os.path.exists(module.path):
            raise OSError('{} already exists...'.format(module.path))
        module.run_hook('precreatemodule')

        if utils.is_git_repo(path):
            self.git.clone(
                path,
                module.path,
                git_branch
            )
        elif utils.is_module(path):
            shutil.copytree(unipath(path), module.path)
        elif os.path.isfile(path) and path.endswith('.yml'):
            utils.ensure_path_exists(module.path)
            shutil.copy2(path, module.config_path)

        module.run_hook('postcreatemodule')
        return module

    def rem_module(self, name):
        module = self.get_module(name)
        if not module:
            raise Exception('Module {} does not exist'.format(name))
        module.remove()

    def get_module(self, name):
        for module in self.get_modules():
            if module.name == name:
                return module

    def get_modules(self):
        modules = []

        module_names = os.listdir(self.modules_path)
        for name in module_names:
            module_path = unipath(self.modules_path, name)
            if utils.is_module(module_path):
                modules.append(Module(module_path))

        return modules


class Module(BaseEnvironment):

    def __init__(self, path, parent=None):
        super(Module, self).__init__(path)
        self.config_path = self.relative_path('module.yml')
        self.parent = parent
        if not self.parent:
            # Check if this module is in a virtualenv
            parent = VirtualEnvironment(self.relative_path('..', '..'))
            if parent.exists:
                self.parent = parent

        if self.parent:
            self.hook_finder = HookFinder(
                self.hook_path,
                self.parent.hook_path,
                get_global_hook_path()
            )
            self.pip = Pip(unipath(self.parent.bin_path, 'pip'))
        else:
            self.hook_finder = HookFinder(
                self.hook_path,
                get_global_hook_path()
            )
            self.pip = None

        self.git = Git(self.path)

    def __repr__(self):
        return '<Module>({0})'.format(self.path)

    @property
    def command(self):
        '''Command used to launch this application module'''

        cmd = self.config.get('command', None)
        if cmd is None:
            return

        cmd = cmd[platform]
        return cmd['path'], cmd['args']

    @property
    def hook_args(self):
        return self.parent, self

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

    @property
    def variables(self):

        v = {
            'MODULE': self.path,
            'PLATFORM': platform,
            'PYVER': sys.version[:3],
            'ENVIRON': '',
        }

        if self.parent:
            v['ENVIRON'] = self.parent.path

        return v

    @property
    def is_active(self):
        from .api import get_active_modules
        return self in get_active_modules()

    def add_module(self, name, git_repo):
        self.parent.add_module(name, git_repo)

    def activate(self):
        from .api import add_active_module
        self.run_hook('preactivatemodule')
        add_active_module(self)
        self.run_hook('postactivatemodule')

    def remove(self):
        from .api import rem_active_module
        self.run_hook('preremovemodule')
        utils.rmtree(self.path)
        rem_active_module(self)
        self.run_hook('postremovemodule')

    def update(self, updated=None):
        self.run_hook('preupdatemodule')
        self.git.pull(self.path)
        updated = super(Module, self).update(updated)
        self.run_hook('postupdatemodule')
        return updated

    def launch(self, *args, **kwargs):

        logger.debug('Launching ' + self.name)

        launch_kwargs = {
            'shell': False,
            'stdout': None,
            'stdin': None,
            'stderr': None,
            'env': os.environ,
        }

        if platform == 'win':
            detached = 0x00000008  # For windows
            launch_kwargs['creationflags'] = detached

        launch_kwargs.update(kwargs)

        cmd, cmd_args = self.command
        if args:
            command = [cmd] + list(args)
        else:
            command = [cmd] + cmd_args

        try:
            subprocess.Popen(command, **launch_kwargs)
        except OSError:
            logger.debug('Could not find module command: \n\t%s', ' '.join(command))
