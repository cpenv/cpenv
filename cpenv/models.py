# -*- coding: utf-8 -*-

import os
import shutil
import site
import sys
import subprocess
from .hooks import HookFinder, get_global_hook_path
from .utils import unipath
from .deps import Git, Pip
from .log import logger
from . import utils, platform
from .packages import yaml


class BaseEnvironment(object):
    '''Common baseclass for :class:`VirtualEnvironment` and :class:`Module`'''

    def __init__(self, path):
        self.path = unipath(path)
        self.name = os.path.basename(self.path)
        self.config_path = self.relative_path(self.path, 'environment.yml')
        self.hook_path = self.relative_path(self.path, 'hooks')
        self._config = None
        self._environ = None

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
    def config(self):
        if self._config is None:
            with open(self.config_path, 'r') as f:
                self._config = yaml.load(f.read()) or {}

        return self._config

    @property
    def variables(self):
        raise NotImplementedError()

    @property
    def environment(self):
        if self._environ is None:
            self._environ = utils.preprocess_dict(
                self.config.get('environment', {}),
                variables=self.variables,
            )

        return self._environ

    def activate(self):
        raise NotImplementedError()

    def remove(self):
        raise NotImplementedError()

    def update(self, updated=None):

        updated = updated or []

        dependencies = self.config.get('dependencies', {})
        pip_installs = dependencies.get('pip', [])
        git_clones = dependencies.get('git', [])
        modules = dependencies.get('modules', [])

        for package in pip_installs:
            if package in updated:
                continue

            self.pip.update(package)
            updated.append('package')

        for repo, destination in git_clones:
            destination = unipath(self.path, destination)
            if destination in updated:
                continue

            if not os.path.exists(destination):
                self.git.clone(repo, destination)
            else:
                self.git.pull(destination)
            updated.append('destination')

        for repo, name in modules:
            if name in updated:
                continue

            if name not in os.listdir(self.modules_path):
                module = self.add_module(repo, name)
            more_updated = module.update()
            updated.append(name)
            updated.extend(more_updated)

        return updated


class VirtualEnvironment(BaseEnvironment):

    def __init__(self, path):
        super(VirtualEnvironment, self).__init__(path)

        self.modules_path = unipath(self.path, 'modules')
        self.hook_finder = HookFinder(self.hook_path, get_global_hook_path())
        self.pip = Pip(unipath(self.bin_path, 'pip'))
        self.git = Git(self.path)

    def __repr__(self):
        return '<VirtualEnvironment>({0})'.format(self.path)

    @property
    def hook_args(self):
        return self

    @property
    def variables(self):
        return {
            'CPENV_ENVIRON': self.path,
            'CPENV_PLATFORM': platform,
            'CPENV_PYVER': sys.version[:3],
        }

    @property
    def environment(self):
        if self._environ is None:
            environ = self.config.get('environment', {})
            additional = {
                'PATH': [self.bin_path],
                'PYTHONPATH': [self.site_path],
                'CPENV_ACTIVE': [self.path],
                'CPENV_ACTIVE_MODULES': self.active_modules(),
            }
            environ = utils.join_dicts(additional, environ)
            self._environ = utils.preprocess_dict(
                environ,
                variables=self.variables,
            )

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
        shutil.rmtree(self.path)
        self.run_hook('postremove')

    def update(self, updated=None):
        self.run_hook('preupdate')
        self.pip.upgrade('pip')
        self.pip.upgrade('wheel')
        self.pip.upgrade('cpenv')
        updated = super(VirtualEnvironment, self).update(updated)
        self.run_hook('postupdate')
        return updated

    def active_modules(self):
        return os.environ.get('CPENV_ACTIVE_MODULES', '').split()

    def add_active_module(self, module):
        '''Add a module to CPENV_ACTIVE_MODULES environment variable'''

        modules = self.active_modules()
        if module.name not in modules:
            modules.append(module.name)
        os.environ['CPENV_ACTIVE_MODULES'] = ' '.join(modules)

    def rem_active_module(self, module):
        '''Remove a module from CPENV_ACTIVE_MODULES environment variable'''

        modules = self.active_modules()
        if module.name in modules:
            modules.remove(module.name)
        os.environ['CPENV_ACTIVE_MODULES'] = ' '.join(modules)

    def add_module(self, name, git_repo):
        module = Module(unipath(self.modules_path, name))
        module.run_hook('premodulecreate')
        self.git.clone(git_repo, unipath(self.module_path, name))
        module.run_hook('postmodulecreate')

    def rem_module(self, name):
        module = self.get_module(name)
        module.remove()

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


class Module(BaseEnvironment):

    def __init__(self, path, parent=None):
        super(Module, self).__init__(path)
        if parent:
            self.parent
        else:
            self.parent = VirtualEnvironment(unipath(self.path, '..', '..'))
        self.hook_finder = HookFinder(
            self.hook_path,
            self.parent.hook_path,
            get_global_hook_path()
        )
        self.pip = Pip(unipath(self.parent.bin_path, 'pip'))
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
    def variables(self):
        return {
            'CPENV_ENVIRON': self.parent.path,
            'CPENV_MODULE': self.path,
            'CPENV_PLATFORM': platform,
            'CPENV_PYVER': sys.version[:3],
        }

    @property
    def is_active(self):
        return self.name in os.environ.get('CPENV_ACTIVE_MODULES', '').split()

    def add_module(self, name, git_repo):
        self.parent.add_module(name, git_repo)

    def activate(self):
        self.run_hook('premoduleactivate')
        self.parent.add_active_module(self)
        self.run_hook('postmoduleactivate')

    def remove(self):
        self.run_hook('premoduleremove')
        shutil.rmtree(self.path)
        self.parent.rem_active_module(self)
        self.run_hook('postmoduleremove')

    def update(self, updated=None):
        self.run_hook('premoduleupdate')
        updated = super(Module, self).update(updated)
        self.run_hook('postmoduleupdate')
        return updated

    def launch(self, *args, **kwargs):

        logger.debug('Launching ' + self.name)
        self.activate()

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

        subprocess.Popen(command, **launch_kwargs)
