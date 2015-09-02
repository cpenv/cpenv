import os
import site
import sys
import virtualenv
from . import platform, envutils, scripts, shell
from .utils import unipath


def get_home_path(platform=platform):
    '''Returns the path to CPENV_HOME for the current platform.
    '''

    home_path = os.environ.get('CPENV_HOME', '~/.cpenv')
    return unipath(home_path, platform)


def get_active_env():
    '''Returns the active environment'''

    active_env = os.environ.get('ACTIVE_ENV', None)
    if active_env:
        return VirtualEnvironment(active_env)
    return None


def get_environments():
    '''Returns a list of VirtualEnvironment objects in CPENV_HOME'''

    home_path = get_home_path()
    if not os.path.exists(home_path):
        return None

    envs = []
    for d in os.listdir(home_path):
        if d == '.wheelhouse':
            continue
        envs.append(VirtualEnvironment(unipath(home_path, d)))

    return envs


def get_environment_named(name, platform=platform):
    '''Returns a VirtualEnvironment object of the specified name.

    :param name: Name of the environment to lookup
    :param platform: Platform to use in lookup (default: current platform)
    '''

    env_root = unipath(get_home_path(platform), name)

    if os.path.exists(env_root):
        return VirtualEnvironment(env_root)

    raise NameError('{} does not exist for platform {}'.format(name, platform))


def create_environment_named(name, config=None):
    '''Create a virtual environment with a specified name in CPENV_HOME.

    :param name: Name of the environment to create
    '''

    env_root = unipath(get_home_path(), name)

    if not os.path.exists(env_root):
        raise EnvironmentError('{} already exists.'.format(name))

    return create_environment(env_root, config)


def create_environment(root, config=None):
    '''Create a virtual envrionment in the specified root.

    :param root: Root path for new environment
    :param config: Optional environment configuration to use for post creation
    '''

    if os.path.exists(root):
        raise EnvironmentError('{} already exists.'.format(name))

    virtualenv.create_environment(root)

    if config:
        _post_create(root, config)

    return VirtualEnvironment(root)


def _post_create(root, config):
    # Do post create
    pass


def deactivate():
    # Deactivate active evironment
    pass


def deactivate_script():
    deactivate()
    script = scripts.restore_env(**os.environ.data)


class VirtualEnvironment(object):

    def __init__(self, root):

        if not os.path.exists(root):
            raise EnvironmentError('{} does not exist'.format(root))

        self.root = unipath(root)
        self.env_file = unipath(root, 'environment.yml')
        self.name = os.path.basename(root)
        self.modules_root = unipath(root, 'modules')

    def __eq__(self, other):
        if isinstance(other, VirtualEnvironment):
            return self.root == other.root
        return self.root == other

    def __repr__(self):
        return '<VirtualEnvironment>({})'.format(self.name)

    def _pre_activate(self):
        '''Prior to activating, store everything necessary to deactivate this
        environment.
        '''

        if not '_CLEAN_ENV' in os.environ:
            if platform == 'win':
                os.environ['PROMPT'] = '$P$G'
            else:
                os.environ['PS1'] = '\u@\h:\w\$'
            os.environ['_PYPREFIX'] = sys.prefix
            clean_env_path = envutils.get_store_env_tmp()
            os.environ['_CLEAN_ENV'] = clean_env_path
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
        os.environ['PATH'] = bin_path + os.pathsep + old_path

        old_pypath = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = site_path + os.pathsep + ''

        old_syspath = set(sys.path)
        site.addsitedir(site_path)
        site.addsitedir(bin_path)
        new_syspaths = set(sys.path) - old_syspath
        for path in new_syspaths:
            sys.path.remove(path)
            sys.path.insert(1, path)

        sys.real_prefix = sys.prefix
        sys.prefix = self.root

        os.environ['WHEELHOUSE'] = self.wheelhouse
        os.environ['PIP_FIND_LINKS'] = self.wheelhouse
        os.environ['PIP_WHEEL_DIR'] = self.wheelhouse
        os.environ['ACTIVE_ENV'] = self.root

    def _post_activate(self):
        '''Setup environment based on environment.yml file'''

        if os.path.exists(self.env_file):
            envutils.set_env_from_file(self.env_file)

    @property
    def wheelhouse(self):

        wheelhouse = unipath(get_home_path(), '.wheelhouse')
        if not os.path.exists(wheelhouse):
            os.makedirs(wheelhouse)
        return wheelhouse

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

        script.extend(scripts.set_env(**os.environ.data))

        return script

    def get_application_modules(self):
        modules = []
        for d in os.listdir(self.modules_root):
            modules.append(ApplicationModule(unipath(self.modules_root, d)))
        return modules


class ApplicationModule(object):

    def __init__(self, root):
        self.root = root
        self.name = os.path.basename(self.root)
        self.env_file = unipath(self.root, 'environment.yml')

    def __repr__(self):
        return '<ApplicationModule>({})'.format(self.name)

    def load(self):
        if os.path.exists(self.env_file):
            # Apply environment
            pass

    def launch(self):
        # Apply module environment and launch application
        pass
