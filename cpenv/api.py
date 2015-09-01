# -*- coding: utf-8 -*-
import collections
import os
import tempfile
import virtualenv
import random
import shutil
import sys
import site
from .vendor import yaml
from .utils import unipath
from . import platform, deps


def get_home_path():
    '''Returns CPENV_HOME path'''

    cpenv_home = os.environ.get('CPENV_HOME', unipath('~/.cpenvs'))
    return unipath(cpenv_home, platform)


def get_active_env():
    '''Returns the active environment'''

    return os.environ.get('ACTIVE_ENV', None)


def get_env_path(name_or_path):
    '''Returns the full path for an environment. If there are path separators
    we return a normalized path. If there are no path separators we return
    name_or_path within your CPENV_HOME director.'''

    if '/' in name_or_path or '\\' in name_or_path:
        return unipath(name_or_path)
    return unipath(get_home_path(), name_or_path)


def get_wheelhouse():
    '''Returns the os specific path to cpenv wheelhouse'''

    wheelhouse = unipath(get_home_path(), '.wheelhouse')
    if not os.path.exists(wheelhouse):
        os.makedirs(wheelhouse)
    return wheelhouse


def get_environments():
    '''Returns a list of environments in your cpenv home path'''

    envs = []

    home_path = get_home_path()
    if not os.path.exists(home_path):
        return envs

    for f in os.listdir(home_path):
        if os.path.isdir(os.path.join(home_path, f)):
            if f == '.wheelhouse':
                continue
            envs.append(f)

    return envs


def activate(name_or_path):
    '''Activate a virtual environment in your CPENV_HOME path.'''

    env_path = get_env_path(name_or_path)

    if not os.path.exists(env_path):
        raise EnvironmentError('No Environment: {}'.format(env_path))

    active_env = get_active_env()
    if active_env:
        deactivate()

    if not '_CLEAN_ENV' in os.environ:
        clean_env_path = store_env()
        set_envvar('_CLEAN_ENV', clean_env_path)

    if platform == 'win':
        site_path = unipath(env_path, 'Lib', 'site-packages')
        bin_path = unipath(env_path, 'Scripts')
    else:
        py_ver = 'python{}'.format(sys.version[:3])
        site_path = unipath(env_path, 'lib', py_ver, 'site-packages')
        bin_path = unipath(env_path, 'bin')

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
    sys.prefix = env_path

    wheelhouse = get_wheelhouse()
    set_envvar('WHEELHOUSE', wheelhouse)
    set_envvar('PIP_FIND_LINKS', wheelhouse)
    set_envvar('PIP_WHEEL_DIR', wheelhouse)
    set_envvar('ACTIVE_ENV', env_path)

    env_file = unipath(env_path, 'environment.yml')
    if os.path.exists(env_file):
        set_env_from_file(env_file)


def deactivate():
    '''Deactivate the current virtual environment'''


    active_env = get_active_env()
    for path in sys.path[:]:
        if path.startswith(active_env):
            sys.path.remove(path)

    restore_env_from_file(os.environ['_CLEAN_ENV'])


def remove(name_or_path):
    '''Remove an environment in CPENV_HOME.'''

    env_path = get_env_path(name_or_path)
    if not os.path.exists(env_path):
        raise EnvironmentError('No Environment {}'.format(env_path))
    active_env = get_active_env()
    if active_env == env_path:
        deactivate()

    shutil.rmtree(env_path)


def create(name_or_path, config=None, **kwargs):
    '''Create an environment in your CPENV_HOME directory. Optionally pass
    a yaml configuration file to use in configuring the new environment.

    :param name: Name of the environment to create
    :param config: Path to a yaml configuration file
    '''

    env_path = get_env_path(name_or_path)

    if os.path.exists(env_path):
        raise EnvironmentError('Environment exists: {}'.format(env_path))

    virtualenv.create_environment(env_path, **kwargs)

    if config and os.path.exists(config):
        config_dict = {}
        with open(config, 'r') as f:
            config_dict.update(yaml.load(f.read()))

        _post_create(env_path, config, config_dict)

    return env_path


def _post_create(env_path, config_path, config):

    environment = config.get('environment', None)
    dependencies = config.get('dependencies', None)

    if environment:
        with open(unipath(env_path, 'environment.yml'), 'w') as f:
            f.write(yaml.dump(environment, default_flow_style=False))

    if dependencies:
        pip_installs = dependencies.get('pip', [])
        git_clones = dependencies.get('git', [])
        includes = dependencies.get('include', [])

        for package in pip_installs:
            deps.pip_install(env_path, package)

        for repo, destination in git_clones:
            deps.git_clone(repo, unipath(env_path, destination))

        for source, destination in includes:
            deps.copy_tree(unipath(config_path, '..', source),
                           unipath(env_path, destination))


def get_store_env_tmp():
    '''Returns an unused random filepath.'''

    tempdir = tempfile.gettempdir()
    temp_name = 'envstore{0:0>3d}'
    temp_path = unipath(tempdir, temp_name.format(random.getrandbits(9)))
    if not os.path.exists(temp_path):
        return temp_path
    else:
        return get_store_env_tmp()


def store_env(path=None):
    '''Encode current environment as yaml and store in path or a temporary
    file. Return the path to the stored environment.
    '''

    path = path or get_store_env_tmp()

    env_dict = yaml.safe_dump(os.environ.data, default_flow_style=False)

    with open(path, 'w') as f:
        f.write(env_dict)
    return path


def set_envvar(var, value):
    '''Set an environment variable.

    :param var: Environment variable to set
    :param value: Value of the variable'''

    if isinstance(value, basestring):
        os.environ[var] = str(unipath(value))
    elif isinstance(value, collections.Sequence):
        paths = [unipath(path) for path in value]
        old_value = os.environ.get(var, None)
        if old_value:
            old_paths = old_value.split(os.pathsep)
            for path in old_paths:
                if not path in paths:
                    paths.append(path)
        os.environ[var] = str(os.pathsep.join(paths))
    elif isinstance(value, (int, long, float)):
        os.environ[var] = str(value)
    elif isinstance(value, dict):
        if platform in value:
            set_envvar(var, value[platform])
        else:
            raise EnvironmentError(
                "Failed to set {}={}\n <type 'dict'> values must include "
                "platforms win, linux, osx".format(var, value))
    else:
        typ = type(value)
        raise EnvironmentError(
            'Environment variables must be sequences, strings or numbers.\n'
            'Received type: {} for var {}'.format(typ, var))


def unset_envvar(var):
    if var in os.environ:
        os.environ.pop(var)


def set_env(**env_dict):
    '''Set environment variables in the current python process from a dict
    containing envvars and values.'''

    for k, v in env_dict.iteritems():
        set_envvar(k, v)


def set_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.load(f.read())

    set_env(**env_dict)
    for k, v in os.environ.items():
        os.environ[k] = unipath(v) # Expand all paths


def restore_env(**env_dict):
    '''Set environment variables in the current python process from a dict
    containing envvars and values.'''

    unset_variables = set(os.environ.keys()) - set(env_dict.keys())
    for envvar in unset_variables:
        unset_envvar(envvar)

    for k, v in env_dict.iteritems():
        set_envvar(k, v)


def restore_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.load(f.read())

    restore_env(**env_dict)
