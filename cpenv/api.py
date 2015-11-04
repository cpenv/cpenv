# -*- coding: utf-8 -*-

import logging
import os
import site
import shutil
import subprocess
import sys
import virtualenv
from . import platform, envutil, shell
from envutil import environ
from .util import unipath, walk_dn
from .packages import yaml

logger = logging.getLogger('cpenv')


def get_home_path(platform=platform):
    '''Returns the path to CPENV_HOME for the current platform.'''

    home_path = environ.get('CPENV_HOME', '~/.cpenv')
    home_platform_path = unipath(home_path, platform)
    if not os.path.exists(home_platform_path):
        try:
            os.makedirs(home_platform_path)
        except:
            pass
    return unipath(home_path, platform)


def get_active_env():
    '''Returns the active environment'''

    active_env = environ.get('CPENV_ACTIVE', None)
    if active_env:
        return VirtualEnvironment(active_env)
    return None


def get_home_environment(name):
    '''Get an environment by name residing in CPENV_HOME'''

    home_env = unipath(get_home_path(), name)
    if not os.path.exists(home_env):
        raise NameError('No environment named {0} in CPENV_HOME'.format(name))

    return VirtualEnvironment(home_env)


def get_home_environments():
    '''Returns a list of VirtualEnvironment objects in CPENV_HOME'''

    home_path = get_home_path()
    if not os.path.exists(home_path):
        return None

    envs = []
    for d in os.listdir(home_path):
        if not os.path.isdir(unipath(home_path, d)):
            continue
        envs.append(VirtualEnvironment(unipath(home_path, d)))

    return envs


def get_environments(name=None, root=None):
    '''Lookup virtualenvs in cache and in CPENV_HOME. Return all environments
    in the cache and cpenv_home if neither name or root arguments are passed.

    :param name: Lookup environment by name
    :param root: Lookup environment by root
    '''

    if not name and not root:
        return list(CACHE.union(set(get_home_environments())))

    if root:
        root = unipath(root)
        if os.path.exists(root):
            env = VirtualEnvironment(root)
            CACHE.add(env)
            CACHE.save()
            return [env]
    else:
        root = '_FALSE_'

    found = set()
    for env in CACHE:
        if env.name == name or env.root.startswith(root):
            found.add(env)

    for env in get_home_environments():
        if env.name == name or env.root.startswith(root):
            found.add(env)

    return list(found)


def create_environment(name=None, root=None, config=None):
    '''Create a virtual envrionment in the specified root.

    :param name: Name of the environment to create in cpenv_home
    :param root: Root path for new environment
    :param config: Optional environment configuration to use for post creation
    '''

    if not name and not root:
        raise ValueError('Must pass either name or root keyword argument')

    if name:
        root = unipath(get_home_path(), name)

    if os.path.exists(root):
        raise EnvironmentError('{0} already exists.'.format(name))

    virtualenv.create_environment(root)
    env = VirtualEnvironment(root)

    os.makedirs(os.path.join(env.root, 'appmodules'))

    if config and not os.path.exists(config):
        logger.debug('Config does not exist: {0}'.format(config))
        _post_create(env)

    try:
        _post_create(env, config)
    except:
        logger.debug('Failed to configure environment...')
        raise

    CACHE.add(env)
    CACHE.save()

    return env


def _post_create(env, config_path=None):
    '''Configures a virtualenv using the passed configuration file'''

    env.pip_update('pip')
    env.pip_update('wheel')

    if not config_path:
        return

    with open(config_path, 'r') as f:
        config = yaml.load(f.read())

    environment = config.get('environment', None)
    dependencies = config.get('dependencies', None)

    if environment:
        with open(unipath(env.root, 'environment.yml'), 'w') as f:
            f.write(yaml.dump(environment, default_flow_style=False))

    if dependencies:
        env.install_dependencies(**dependencies)


def deactivate():
    '''Deactivates an environment by restoring all env vars to a clean state
    stored prior to activating environments
    '''

    if not 'CPENV_ACTIVE' in environ:
        return
    if not 'CPENV_CLEAN_ENV' in environ:
        raise EnvironmentError('Can not deactivate environment...')

    envutil.restore_env_from_file(environ['CPENV_CLEAN_ENV'])


class VirtualEnvironment(object):
    '''Manage a virtual environment'''

    def __init__(self, root):

        self.root = unipath(root)
        self.env_file = unipath(root, 'environment.yml')
        self.name = os.path.basename(root)
        self.modules_root = unipath(root, 'appmodules')

    def __eq__(self, other):
        if isinstance(other, VirtualEnvironment):
            return self.root == other.root
        return self.root == other

    def __hash__(self):
        return hash(self.root)

    def __repr__(self):
        return '<VirtualEnvironment>({0})'.format(self.name)

    def _pre_activate(self):
        '''Prior to activating, store everything necessary to deactivate this
        environment.
        '''

        if not 'CPENV_CLEAN_ENV' in environ:
            if platform == 'win':
                environ['PROMPT'] = '$P$G'
            else:
                environ['PS1'] = '\u@\h:\w\$'
            clean_env_path = envutil.get_store_env_tmp()
            environ['CPENV_CLEAN_ENV'] = clean_env_path
            envutil.store_env(path=clean_env_path)

    def _activate(self):
        '''Active this environment.'''

        if platform == 'win':
            site_path = unipath(self.root, 'Lib', 'site-packages')
            bin_path = unipath(self.root, 'Scripts')
        else:
            py_ver = 'python{0}'.format(sys.version[:3])
            site_path = unipath(self.root, 'lib', py_ver, 'site-packages')
            bin_path = unipath(self.root, 'bin')

        old_path = environ.get('PATH', '')
        environ['PATH'] = self.bin_path + os.pathsep + old_path

        old_pypath = environ.get('PYTHONPATH', '')
        environ['PYTHONPATH'] = self.site_path + os.pathsep + ''

        old_syspath = set(sys.path)
        site.addsitedir(self.site_path)
        site.addsitedir(self.bin_path)
        new_syspaths = set(sys.path) - old_syspath
        for path in new_syspaths:
            sys.path.remove(path)
            sys.path.insert(1, path)

        sys.real_prefix = sys.prefix
        sys.prefix = self.root

        environ['CPENV_ACTIVE'] = self.root

    def _post_activate(self):
        '''Setup environment based on environment.yml file'''

        if os.path.exists(self.env_file):
            envutil.set_env_from_file(self.env_file)

    def activate(self):
        '''Activate this environment'''

        active_env = get_active_env()

        if active_env == self:
            return
        else:
            deactivate()

        self._pre_activate()
        self._activate()
        self._post_activate()

    def remove(self):
        '''Permanently remove this virtual environment from disk'''

        try:
            shutil.rmtree(self.root)
            return True
        except:
            raise

    def install_dependencies(self, **dependencies):
        '''Install dependencies in an environment'''

        pip_installs = dependencies.get('pip', [])
        git_clones = dependencies.get('git', [])
        app_modules = dependencies.get('appmodules', [])

        for package in pip_installs:
            self.pip_update(package)

        for repo, destination in git_clones:

            if not destination.startswith(self.root):
                destination = unipath(self.root, destination)

            if not os.path.exists(destination):
                self.git_clone(repo, destination)

        for repo, name in app_modules:

            if name in [m.name for m in self.get_application_modules()]:
                continue

            app_module = self.add_application_module(repo, name)
            if app_module and app_module.dependencies:
                self.install_dependencies(**app_module.dependencies)

    def update(self, config_path=None):
        '''Install dependencies in an environment'''

        if config_path:
            _post_create(self, config_path)

        self.pip_update_all()

        for repo_path in self.get_git_deps():
            logger.debug('Updating ' + repo_path)
            self.git_pull(repo_path)

        for app_module in self.get_application_modules():
            logger.debug('Updating ' + app_module.root)
            self.git_pull(app_module.root)
            if app_module.dependencies:
                self.install_dependencies(**app_module.dependencies)

    @property
    def site_path(self):
        '''Path to environments site-packages'''

        if platform == 'win':
            return unipath(self.root, 'Lib', 'site-packages')

        py_ver = 'python{0}'.format(sys.version[:3])
        return unipath(self.root, 'lib', py_ver, 'site-packages')

    @property
    def bin_path(self):
        '''Path to environments bin'''

        if platform == 'win':
            return unipath(self.root, 'Scripts')

        return unipath(self.root, 'bin')

    @property
    def exists(self):
        '''Does this environments root path exist?'''

        return os.path.exists(self.root)

    @property
    def is_active(self):
        active_root = os.environ.get('CPENV_ACTIVE', None)

        if not active_root:
            return False

        return os.path.samefile(self.root, active_root)

    @property
    def is_valid(self):
        '''Does this environment include a site-packages and bin directory'''

        return os.path.exists(self.site_path) and os.path.exists(self.bin_path)

    @property
    def pip_path(self):
        '''Returns path to pip for current environment'''

        return unipath(self.bin_path, 'pip')

    def pip_wheel(self, package):

        return shell.run(self.pip_path, 'wheel', package)

    def pip_install(self, package):
        '''Quietly install a python package using pip to'''

        self.pip_wheel(package)
        return shell.run(self.pip_path, 'install', package)

    def pip_update(self, package):
        '''Update a python package using pip to'''

        logger.debug('Updating ' + package)
        self.pip_wheel(package)
        return shell.run(self.pip_path, 'install', '-U' package)

    def pip_update_all(self):
        '''Update all installed python packages'''

        pip_list_output = subprocess.check_output(self.pip_path + ' list')
        packages = [l.split(' ')[0] for l in pip_list_output.split('\n') if l]
        for package in packages:
            self.pip_update(package)

    def git_clone(self, repo, destination):
        '''Clone a repository to a destination relative to envrionment root'''

        if not destination.startswith(self.root):
            destination = unipath(self.root, destination)

        return shell.run('git', 'clone', repo, destination)

    def git_pull(self, repo_path, *args):
        '''Clone a repository to a destination relative to envrionment root'''

        if not repo_path.startswith(self.root):
            repo_path = unipath(self.root, repo_path)

        return shell.run('git', 'pull', *args, **{'cwd':repo_path})

    def copy_tree(self, source, destination):
        '''Copy a tree to a destination relative to environment root'''

        if not destination.startswith(self.root):
            destination = unipath(self.root, destination)

        try:
            shutil.copytree(source, destination)
        except:
            logger.debug('Failed to include ' + source)

    def get_git_deps(self, depth=10):
        '''Get all git repositories within this environment'''

        repos = []

        for root, subdirs, files in walk_dn(self.root, depth=depth):
            if 'appmodules' in root:
                continue
            if '.git' in subdirs:
                repos.append(root)

        return repos

    def get_application_modules(self):
        '''Get all ApplicationModules this environment contains'''

        modules = []
        for d in os.listdir(self.modules_root):
            modules.append(ApplicationModule(unipath(self.modules_root, d)))
        return modules

    def get_application_module(self, name):
        '''Get an ApplicationModule by name'''

        for mod in self.get_application_modules():
            if mod.name == name:
                return mod

    def add_application_module(self, repo, name):
        '''Add a new application module to this environment.

        :param repo: Repository path to application module
        :param name: Name to use for application module
        '''

        if not os.path.exists(self.modules_root):
            os.makedirs(self.modules_root)

        if name in [m.name for m in self.get_application_modules()]:
            logger.debug('Application Module {0} already exists'.format(name))
            return

        app_root = unipath(self.modules_root, name)
        self.git_clone(repo, app_root)
        return ApplicationModule(app_root)

    def rem_application_module(self, name):
        '''Remove an application module by name'''

        mod = self.get_application_module(name)
        if mod:
            mod.remove()


class ApplicationModule(object):

    def __init__(self, root):
        self.root = root
        self.name = os.path.basename(self.root)
        self.mod_file = unipath(self.root, 'appmodule.yml')
        self._data = None
        self._launch_cmd = None

    def __eq__(self, other):
        if isinstance(other, ApplicationModule):
            return self.root == other.root
        return self.root == other

    def __hash__(self):
        return hash(self.root)

    def __repr__(self):
        return '<ApplicationModule>({0})'.format(self.name)

    @property
    def is_active(self):
        active_app_root = os.environ.get('CPENV_APP', None)

        if not active_app_root:
            return False

        return os.path.samefile(self.root, active_app_root)

    @property
    def is_module(self):
        '''Is this really an application module?'''

        return os.path.exists(self.mod_file)

    @property
    def data(self):
        '''All the data stored in appmodule.yml'''

        if not self._data:
            with open(self.mod_file, 'r') as f:
                self._data = yaml.load(f.read())
        return self._data

    @property
    def command(self):
        '''Command used to launch this application module'''

        cmd = self.data.get('command', None)
        if cmd:
            cmd = cmd[platform]
            return [cmd['path']] + cmd['args']

    @property
    def environment(self):
        '''Dict containing environment variables'''

        return self.data.get('environment', None)

    @property
    def dependencies(self):
        '''List containing dependencies'''

        return self.data.get('dependencies', None)

    def remove(self):
        '''Permanently remove this environment from disk'''

        shutil.rmtree(self.root)

    def activate(self):
        '''Active this application modules environment configured in
        appmodule.yml
        '''

        if not self.is_module:
            return
        environ['CPENV_APP'] = self.root
        envutil.set_env(self.environment)

    def launch(self):
        '''Launch this application module. Launch command configured in
        appmodule.yml
        '''

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
            detached = 0x00000008 # For windows
            launch_kwargs['creationflags'] = detached

        subprocess.Popen(self.command, **launch_kwargs)


class EnvironmentCache(set):
    '''Cache VirtualEnvironment objects to disk.'''

    def __init__(self, path):
        super(EnvironmentCache, self).__init__()
        self.path = path

        if not os.path.exists(self.path):
            root = os.path.dirname(self.path)
            if not os.path.exists(root):
                os.makedirs(root)
            with open(self.path, 'a'):
                os.utime(self.path, None)
        else:
            self.load()
            self.validate()

    def validate(self):
        '''Validate all the entries in the environment cache.'''

        for env in list(self):
            if not env.exists or not env.is_valid:
                self.remove(env)

    def load(self):
        '''Load the environment cache from disk.'''

        if not os.path.exists(self.path):
            return

        with open(self.path, 'r') as f:
            env_data = yaml.load(f.read())

        if env_data:
            for env in env_data:
                self.add(VirtualEnvironment(env['root']))

    def clear(self):
        '''Clear the environment cache'''
        for env in list(self):
            self.remove(env)

    def save(self):
        '''Save the environment cache to disk.'''

        env_data = [dict(name=env.name, root=env.root) for env in self]
        encode = yaml.safe_dump(env_data, default_flow_style=False)

        with open(self.path, 'w') as f:
            f.write(encode)

# Instantiate EnvironmentCache
CACHE = EnvironmentCache(unipath('~/.cpenv', 'envcache.yml'))
