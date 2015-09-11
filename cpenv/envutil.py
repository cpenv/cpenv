import collections
import os
import random
import sys
import tempfile
from string import Template
from .util import unipath
from .packages import yaml
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


def restore_env(env_dict):
    '''Set environment variables in the current python process from a dict
    containing envvars and values.'''

    if hasattr(sys, 'real_prefix'):
        sys.prefix = sys.real_prefix
        del(sys.real_prefix)

    os.environ.data = expand_env(dict_to_env(env_dict))


def restore_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.load(f.read())

    restore_env(env_dict)


def set_env(*env_dicts):
    '''Set environment variables in the current python process from a dict
    containing envvars and values.'''

    old_env_dict = env_to_dict(os.environ.data)
    new_env_dict = dict_join(old_env_dict, *env_dicts)
    new_env = dict_to_env(new_env_dict)
    os.environ.data = expand_env(new_env)


def set_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.load(f.read())

    if 'environment' in env_dict:
        env_dict = env_dict['environment']

    set_env(env_dict)


def dict_join(*dicts):
    out_dict = {}

    for d in dicts:
        for k, v in d.iteritems():
            if isinstance(v, dict):
                out_dict[k] = v[platform]
            elif isinstance(v, (int, float, long)):
                out_dict[k] = str(v)
            elif isinstance(v, basestring):
                out_dict[k] = v
            elif isinstance(v, unicode):
                out_dict[k] = str(v)
            elif isinstance(v, (list, tuple, set)):
                if not k in out_dict:
                    out_dict[k] = list(v)
                elif isinstance(out_dict[k], list):
                    for item in v:
                        if not item in out_dict[k]:
                            out_dict[k].insert(0, item)
                elif isinstance(out_dict[k], basestring):
                    v.append(out_dict[k])
                    out_dict[k] = v
            else:
                raise TypeError('{} not a valid value type'.format(type(v)))

    return out_dict


def env_to_dict(env, pathsep=os.pathsep):
    out_dict = {}

    for k, v in env.iteritems():
        if pathsep in v:
            out_dict[k] = v.split(pathsep)
        else:
            out_dict[k] = v

    return out_dict


def dict_to_env(env, pathsep=os.pathsep):
    out_env = {}

    for k, v in env.iteritems():
        if isinstance(v, list):
            out_env[k] = pathsep.join(v)
        elif isinstance(v, basestring):
            out_env[k] = v
        else:
            raise TypeError('{} not a valid env var type'.format(type(v)))

    return out_env


def expand_env(env):

    out_env = {}

    # Expand
    for k, v in env.iteritems():
        out_env[k] = Template(v).safe_substitute(env)

    # Again for nested variable references
    for k, v in out_env.items():
        out_env[k] = Template(v).safe_substitute(out_env)

    return out_env
