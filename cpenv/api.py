import logging
import os
import site
import shutil
import subprocess
import sys
import virtualenv
from . import platform, envutils, shell
from .utils import unipath
from .vendor import yaml

logger = logging.getLogger('cpenv')


def get_home_path(platform=platform):
    '''Returns the path to CPENV_HOME for the current platform.
    '''

    home_path = os.environ.get('CPENV_HOME', '~/.cpenv')
    return unipath(home_path, platform)


def get_active_env():
    '''Returns the active environment'''

    active_env = os.environ.get('CPENV_ACTIVE', None)
    if active_env:
        return VirtualEnvironment(active_env)
    return None


def get_home_environment(name=None):

    home_env = unipath(get_home_path(), name)
    if not os.path.exists(home_env):
        raise NameError('No environment named {} in CPENV_HOME'.format(name))

    return VirtualEnvironment(home_env)


def get_home_environments():
    '''Returns a list of VirtualEnvironment objects in CPENV_HOME'''

    home_path = get_home_path()
    if not os.path.exists(home_path):
        return None

    envs = []
    for d in os.listdir(home_path):
        if d == '.wheelhouse' or not os.path.isdir(unipath(home_path, d)):
            continue
        envs.append(VirtualEnvironment(unipath(home_path, d)))

    return envs


def get_environments(name=None, root=None):

    if not name and not root:
        return list(ENV_CACHE.union(set(get_home_environments())))

    if root:
        root = unipath(root)
        if os.path.exists(root):
            env = VirtualEnvironment(root)
            ENV_CACHE.add(env)
            ENV_CACHE.save()
            return [env]
    else:
        root = '_FALSE_'

    found = set()
    for env in ENV_CACHE:
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
        raise EnvironmentError('{} already exists.'.format(name))

    virtualenv.create_environment(root)
    env = VirtualEnvironment(root)

    if config and not os.path.exists(config):
        logger.debug('Config does not exist: {}'.format(config))
    if config:
        try:
            _post_create(env, config)
        except:
            logger.debug('Failed to configure environment...')
            raise

    ENV_CACHE.add(env)
    ENV_CACHE.save()

    return env


def _post_create(env, config_path):

    with open(config_path, 'r') as f:
        config = yaml.load(f.read())

    environment = config.get('environment', None)
    dependencies = config.get('dependencies', None)

    if environment:
        with open(unipath(env.root, 'environment.yml'), 'w') as f:
            f.write(yaml.dump(environment, default_flow_style=False))

    if dependencies:
        _install_dependencies(env, dependencies, os.path.dirname(config_path))


def _install_dependencies(env, dependencies, root):
    pip_installs = dependencies.get('pip', [])
    git_clones = dependencies.get('git', [])
    app_modules = dependencies.get('appmodules', [])
    includes = dependencies.get('include', [])

    for package in pip_installs:
        env.pip_install(package)

    for repo, destination in git_clones:
        env.git_clone(repo, destination)

    for repo, name in app_modules:
        app_module = env.add_application_module(repo, name)
        if app_module.dependencies:
            _install_dependencies(
                env,
                app_module.dependencies,
                app_module.root)

    for source, destination in includes:
        env.copy_tree(unipath(root, source), destination)


def deactivate():
    if not 'CPENV_ACTIVE' in os.environ:
        return
    if not 'CPENV_CLEAN_ENV' in os.environ:
        raise EnvironmentError('Can not deactivate environment...')

    clean_env_path = os.environ.get('CPENV_CLEAN_ENV')

    with open(clean_env_path, 'r') as f:
        env_data = yaml.load(f.read())

    envutils.restore_env_from_file(clean_env_path)


def deactivate_script():
    if not 'CPENV_ACTIVE' in os.environ:
        return
    if not 'CPENV_CLEAN_ENV' in os.environ:
        raise EnvironmentError('Can not deactivate environment...')

    return shell.envutils.restore_env_from_file(os.environ['CPENV_CLEAN_ENV'])


class VirtualEnvironment(object):

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
        return '<VirtualEnvironment>({})'.format(self.name)

    def _pre_activate(self):
        '''Prior to activating, store everything necessary to deactivate this
        environment.
        '''

        if not 'CPENV_CLEAN_ENV' in os.environ:
            if platform == 'win':
                os.environ['PROMPT'] = '$P$G'
            else:
                os.environ['PS1'] = '\u@\h:\w\$'
            os.environ['_PYPREFIX'] = sys.prefix
            clean_env_path = envutils.get_store_env_tmp()
            os.environ['CPENV_CLEAN_ENV'] = clean_env_path
            envutils.store_env(path=clean_env_path)

    def _activate(self):
        '''Active this environment.'''

        # Setup Terminal Prompts
        if platform == 'win':
            os.environ['PROMPT'] = '[{}] $P$G'.format(self.name)
        else:
            os.environ['PS1'] = '[{}] \u@\h:\w\$'.format(self.name)

        # Activate Environment

        if platform == 'win':
            site_path = unipath(self.root, 'Lib', 'site-packages')
            bin_path = unipath(self.root, 'Scripts')
        else:
            py_ver = 'python{}'.format(sys.version[:3])
            site_path = unipath(self.root, 'lib', py_ver, 'site-packages')
            bin_path = unipath(self.root, 'bin')

        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = self.bin_path + os.pathsep + old_path

        old_pypath = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = self.site_path + os.pathsep + ''

        old_syspath = set(sys.path)
        site.addsitedir(self.site_path)
        site.addsitedir(self.bin_path)
        new_syspaths = set(sys.path) - old_syspath
        for path in new_syspaths:
            sys.path.remove(path)
            sys.path.insert(1, path)

        sys.real_prefix = sys.prefix
        sys.prefix = self.root

        os.environ['WHEELHOUSE'] = self.wheelhouse
        os.environ['PIP_FIND_LINKS'] = self.wheelhouse
        os.environ['PIP_WHEEL_DIR'] = self.wheelhouse
        os.environ['CPENV_ACTIVE'] = self.root

    def _post_activate(self):
        '''Setup environment based on environment.yml file'''

        if os.path.exists(self.env_file):
            envutils.set_env_from_file(self.env_file)

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

    def activate_script(self):
        '''Generate Activate Shell Script'''

        self.activate()

        script = shell.ShellScript()
        if platform != 'win':
            script.run_cmd('export PS1')

        script.extend(shell.envutils.set_env(**os.environ.data))

        return script

    def remove(self):
        try:
            shutil.rmtree(self.root)
            ENV_CACHE.remove(self)
            ENV_CACHE.save()
            return True
        except:
            raise

    @property
    def site_path(self):
        if platform == 'win':
            return unipath(self.root, 'Lib', 'site-packages')

        py_ver = 'python{}'.format(sys.version[:3])
        return unipath(self.root, 'lib', py_ver, 'site-packages')

    @property
    def bin_path(self):
        if platform == 'win':
            return unipath(self.root, 'Scripts')

        return unipath(self.root, 'bin')

    @property
    def exists(self):
        return os.path.exists(self.root)

    @property
    def is_valid(self):
        return os.path.exists(self.site_path) and os.path.exists(self.bin_path)

    @property
    def wheelhouse(self):

        wheelhouse = unipath(get_home_path(), '.wheelhouse')
        if not os.path.exists(wheelhouse):
            os.makedirs(wheelhouse)
        return wheelhouse

    @property
    def pip_path(self):
        '''Returns path to pip for current environment'''
        return unipath(self.bin_path, 'pip')

    def pip_install(self, package):
        '''Quietly install a python package using pip to'''

        cmd_args = [self.pip_path, '-q', 'install', package]

        try:
            subprocess.check_call(cmd_args, env=os.environ, shell=True)
            logger.debug('pip installed ' + package)
        except subprocess.CalledProcessError:
            logger.debug('pip failed to install ' + package)

    def git_clone(self, repo, destination):
        '''Clone a repository to a destination relative to envrionment root'''

        if not destination.startswith(self.root):
            destination = unipath(self.root, destination)

        cmd_args = ['git', 'clone', '-q', repo, destination]

        try:
            subprocess.check_call(cmd_args, env=os.environ, shell=True)
            logger.debug('cloned {} to {}'.format(repo, destination))
        except subprocess.CalledProcessError:
            logger.debug('git failed to clone ' + repo)

    def copy_tree(self, source, destination):
        '''Copy a tree to a destination relative to environment root'''

        if not destination.startswith(self.root):
            destination = unipath(self.root, destination)

        try:
            shutil.copytree(source, destination)
        except:
            logger.debug('Failed to include ' + source)

    def add_application_module(self, repo, name):
        if not os.path.exists(self.modules_root):
            os.makedirs(self.modules_root)

        if name in self.get_application_modules():
            logger.debug('Application Module {} already exists'.format(name))
            return

        app_root = unipath(self.modules_root, name)
        self.git_clone(repo, app_root)
        return ApplicationModule(app_root)

    def get_application_modules(self):
        modules = []
        for d in os.listdir(self.modules_root):
            modules.append(ApplicationModule(unipath(self.modules_root, d)))
        return modules


class ApplicationModule(object):

    def __init__(self, root):
        self.root = root
        self.name = os.path.basename(self.root)
        self.mod_file = unipath(self.root, 'appmodule.yml')
        self._data = None
        self._launch_cmd = None

    def __eq__(self, other):
        if isinstance(other, VirtualEnvironment):
            return self.root == other.root
        return self.root == other

    def __hash__(self):
        return hash(self.root)

    def __repr__(self):
        return '<ApplicationModule>({})'.format(self.name)

    @property
    def is_module(self):
        return os.path.exists(self.mod_file)

    @property
    def data(self):
        if not self._data:
            with open(self.mod_file, 'r') as f:
                self._data = yaml.load(f.read())
        return self._data

    @property
    def command(self):
        cmd = self.data.get('command', None)
        if cmd:
            cmd = cmd[platform]
            return [cmd['path']] + cmd['args']

    @property
    def environment(self):
        return self.data.get('environment', None)

    @property
    def dependencies(self):
        return self.data.get('dependencies', None)

    def activate(self):
        if not self.is_module:
            return

        envutils.set_env(**self.environment)

    def launch(self):
        logger.debug('Launching ' + self.name)
        os.environ['CPENV_APP'] = self.root
        self.activate()
        subprocess.Popen(self.command)


class EnvironmentCache(set):

    def __init__(self, path):
        super(EnvironmentCache, self).__init__()
        self.path = path
        self.load()
        self.validate()

    def validate(self):
        for env in list(self):
            if not env.exists or not env.is_valid:
                self.remove(env)

    def load(self):

        if not os.path.exists(self.path):
            return

        with open(self.path, 'r') as f:
            env_data = yaml.load(f.read())

        for env in env_data:
            self.add(VirtualEnvironment(env['root']))

    def save(self):
        env_data = [dict(name=env.name, root=env.root) for env in self]
        encode = yaml.safe_dump(env_data, default_flow_style=False)

        with open(self.path, 'w') as f:
            f.write(encode)

ENV_CACHE = EnvironmentCache(unipath(get_home_path(), '.envcache.yml'))
