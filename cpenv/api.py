import os
import sys
import virtualenv
from .cache import EnvironmentCache
from .resolver import Resolver
from .util import (
    is_system_path, is_environment, is_home_environment, unipath, touch
)
from .envutil import environ
from . import envutil, plaform


def _pre_create(path, config=None):
    pass

def _create(path, config=None):

    virtualenv.create_environment(path)
    env = VirtualEnvironment(path)

    if not is_home_environment(path):
        EnvironmentCache.add(env)


def _post_create(path, config=None):

    config_path = unipath(path, 'environment.yml')
    if not config:
        touch(config_path)
        return

    shutil.copy2(config, config_path)


def create(name_or_path=None, config=None):
    '''Create a virtual environment. You can pass either the name of a new
    environment to create in your CPENV_HOME directory OR specify a full path
    to create an environment outisde your CPENV_HOME.

    Create an environment in CPENV_HOME::

        >>> cpenv.create('myenv')

    Create an environment elsewhere::

        >>> cpenv.create('~/custom_location/myenv')

    :param name_or_path: Name or full path of environment
    :param config: Environment configuration including dependencies etc...
    '''

    if is_system_path(name_or_path):
        path = unipath(name_or_path)
    else:
        path = unipath(get_home_path(), name_or_path)

    _pre_create(path, config=config)
    _create(path, config=config)
    _post_create(path, config=config)

    env = VirtualEnvironment(path)
    return env


def activate(name_or_path, *modules):
    '''Activate a virtual environment by name or path. Additional args refer
    to modules residing in the specified environment that you would
    also like to activate.

    Activate an environment::

        >>> cpenv.activate('myenv')

    Activate an environment with some modules::

        >>> cpenv.activate('myenv', 'maya', 'mtoa', 'vray_for_maya')

    :param name_or_path: Name or full path of environment
    :param modules: Additional modules to activate
    '''

    env = get_environment(name_or_path)
    env.activate()

    if modules:
        activate_modules(*modules)

    return env


def activate_modules(*modules):
    '''After you have activated a virtual environment, use this to activate
    a bunch of the environments modules.

    :param modules: Modules to be activated
    '''

    active = get_active_env()
    if not active:
        raise EnvironmentError('No environment currently active...')

    for module in modules:
        mod = env.get_module(module, None)
        if mod:
            mod.activate()
        else:
            raise EnvironmentError('Could not find module: ' + module)


def deactivate():
    '''Deactivates an environment by restoring all env vars to a clean state
    stored prior to activating environments
    '''

    if not 'CPENV_ACTIVE' in environ:
        return
    if not 'CPENV_CLEAN_ENV' in environ:
        raise EnvironmentError('Can not deactivate environment...')

    envutil.restore_env_from_file(environ['CPENV_CLEAN_ENV'])


def get_home_path():
    home = unipath(os.environ.get('CPENV_HOME', '~/.cpenv'))
    if not os.path.exists(home):
        os.makedirs(home)
    return home


def get_active_env():
    '''Returns the active environment as a VirtualEnvironment instance or
    None if one is not active.
    '''

    active = os.environ.get('CPENV_ACTIVE', None)
    if active:
        return VirtualEnvironment(active)


def get_environments():
    '''Returns a list of all known virtual environments as VirtualEnvironment
    instances. This includes those in CPENV_HOME and any others that are
    cached(created by the current user or activated once by full path.)
    '''

    environments = []

    cwd = os.getcwd()
    for d in os.listdir(cwd):

        if d == 'environment.yml':
            environments.append(VirtualEnvironment(cwd))
            continue

        path = unipath(cwd, d)
        if is_environment(path):
            environments.append(VirtualEnvironment(path))

    home = get_home_path()
    for d in os.listdir(home):

        path = unipath(home, d)
        if is_environment(path):
            environments.append(VirtualEnvironment(path))

    for env in EnvironmentCache:
        environments.append(env)

    return environments


def get_environment(name_or_path):

    resolver = Resolver(name_or_path)
    path = resolver.resolve()
    return VirtualEnvironment(path)


class VirtualEnvironment(object):
    '''Manage a virtual environment'''

    def __init__(self, root):

        self.root = unipath(root)
        self.env_file = unipath(root, 'environment.yml')
        self.name = os.path.basename(root)
        self.modules_root = unipath(root, 'modules')

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
        environ['PYTHONPATH'] = self.site_path + os.pathsep + old_pypath

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

        logger.debug('Installing ' + package)
        return shell.run(self.pip_path, 'install', package)

    def pip_update(self, package):
        '''Update a python package using pip to'''

        logger.debug('Updating ' + package)
        return shell.run(self.pip_path, 'install', '-U', package)

    def pip_update_all(self):
        '''Update all installed python packages'''

        pip_list_output = subprocess.check_output(self.pip_path + ' list')
        packages = [l.split(' ')[0] for l in pip_list_output.split('\n') if l]
        for package in packages:
            self.pip_update(package)

    def git_clone(self, repo, destination):
        '''Clone a repository to a destination relative to envrionment root'''

        logger.debug('Installing ' + repo)
        if not destination.startswith(self.root):
            destination = unipath(self.root, destination)

        return shell.run('git', 'clone', repo, destination)

    def git_pull(self, repo_path, *args):
        '''Clone a repository to a destination relative to envrionment root'''

        logger.debug('Updating ' + repo_path)
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

    def get_modules(self):
        '''Get all Modules this environment contains'''

        modules = []
        for d in os.listdir(self.modules_root):
            modules.append(Module(unipath(self.modules_root, d)))
        return modules

    def get_module(self, name):
        '''Get an Module by name'''

        path = unipath(self.modules_root, name)

        if os.path.exists(path):
            return Module(path)

    def add_module(self, name, repo):
        '''Add a new module to this environment.

        :param repo: Repository path to module
        :param name: Name to use for module
        '''

        if not os.path.exists(self.modules_root):
            os.makedirs(self.modules_root)

        if name in [m.name for m in self.get_application_modules()]:
            logger.debug('Application Module {0} already exists'.format(name))
            return

        app_root = unipath(self.modules_root, name)
        self.git_clone(repo, app_root)
        return Module(app_root)

    def remove_module(self, name):
        '''Remove an module by name'''

        mod = self.get_module(name)
        if mod:
            mod.remove()


class Module(object):

    def __init__(self, root):
        self.root = root
        self.name = os.path.basename(self.root)
        self.mod_file = unipath(self.root, 'module.yml')
        self._data = None
        self._launch_cmd = None

    def __eq__(self, other):
        if isinstance(other, Module):
            return self.root == other.root
        return self.root == other

    def __hash__(self):
        return hash(self.root)

    def __repr__(self):
        return '<Module>({0})'.format(self.name)

    @property
    def is_active(self):
        active_app_root = os.environ.get('CPENV_APP', None)

        if not active_app_root:
            return False

        return os.path.samefile(self.root, active_app_root)

    @property
    def is_module(self):
        '''Is this really an module?'''

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
        '''Command used to launch this module'''

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
        '''Active this modules environment configured in
        appmodule.yml
        '''

        if not self.is_module:
            return
        environ['CPENV_APP'] = self.root
        envutil.set_env(self.environment)

    def launch(self):
        '''Launch this module. Launch command configured in
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
