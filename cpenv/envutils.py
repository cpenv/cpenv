import collections
import os
import random
import sys
import tempfile
from .utils import unipath
from .vendor import yaml
from . import platform


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
        os.environ[k] = os.path.expandvars(v)


def restore_env(**env_dict):
    '''Set environment variables in the current python process from a dict
    containing envvars and values.'''

    if hasattr(sys, 'real_prefix'):
        sys.prefix = sys.real_prefix
        del(sys.real_prefix)

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
