# -*- coding: utf-8 -*-

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

    replace_osenviron(expand_env(dict_to_env(env_dict)))


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
    replace_osenviron(expand_env(new_env))


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


def replace_osenviron(env_dict):
    for k in os.environ.keys():
        if not k in env_dict:
            del os.environ[k]

    for k, v in env_dict.iteritems():
        os.environ[k] = v


def handle_dict(d, k, v):
    '''Add a dict value to an env dict'''

    d[k] = v[platform]

def handle_nonstr(d, k, v):
    '''Add a nonstring value to env dict'''

    d[k] = str(v)

def handle_str(d, k, v):
    '''Add a string value to env dict'''

    d[k] = v

def handle_seq(d, k, v):
    '''Add a sequence value to env dict'''

    if not k in d:
        d[k] = list(v)
    elif isinstance(d[k], list):
        for item in v:
            if not item in d[k]:
                d[k].insert(0, item)
    elif isinstance(d[k], basestring):
        v.append(d[k])
        d[k] = v

def dict_join(*dicts):
    '''Join a bunch of dicts'''

    handlers = {
        dict: handle_dict,
        int: handle_nonstr,
        float: handle_nonstr,
        long: handle_nonstr,
        unicode: handle_nonstr,
        basestring: handle_str,
        str: handle_str,
        list: handle_seq,
        tuple: handle_seq,
        set: handle_seq,
    }

    out_dict = {}

    for d in dicts:
        for k, v in d.iteritems():
            try:
                handlers[type(v)](out_dict, k, v)
            except KeyError:
                raise TypeError('{} not a valid value type'.format(type(v)))

    return out_dict


def env_to_dict(env, pathsep=os.pathsep):
    '''Convert a dict representing environment variables into a standard dict.
    Variables containing multiple values will be split into a pylist based on
    the argument passed to pathsep.

    :param env: Environment dict like os.environ.data
    :param pathsep: Path separator used to split variables
    '''

    out_dict = {}

    for k, v in env.iteritems():
        if pathsep in v:
            out_dict[k] = v.split(pathsep)
        else:
            out_dict[k] = v

    return out_dict


def dict_to_env(dict, pathsep=os.pathsep):
    '''Convert a python dict to a dict containing valid environment variable
    values.

    :param dict: Dict to convert to an env dict
    :param pathsep: Path separator used to join lists(default os.pathsep)
    '''

    out_env = {}

    for k, v in dict.iteritems():
        if isinstance(v, list):
            out_env[k] = pathsep.join(v)
        elif isinstance(v, basestring):
            out_env[k] = v
        else:
            raise TypeError('{} not a valid env var type'.format(type(v)))

    return out_env


def expand_env(env):
    '''Expand all environment variables in an environment dict, like
    os.environ.data.

    :param env: Environment dict
    '''

    out_env = {}

    # Expand
    for k, v in env.iteritems():
        out_env[k] = Template(v).safe_substitute(env)

    # Again for nested variable references
    for k, v in out_env.items():
        out_env[k] = Template(v).safe_substitute(out_env)

    return out_env


class Environ(object):
    '''Makes sure all values being set in os.environ are string type and not
    unicode.'''


    def __init__(self, environ):
        self.environ = environ

    def __getattr__(self, attr):
        return getattr(self.environ, attr)

    def __contains__(self, item):
        return item in self.environ

    if int(sys.version[0]) < 3:

        def __getitem__(self, key):
            return self.environ[key].decode('utf8')

        def __setitem__(self, key, value):
            self.environ[key] = value.encode('utf8')

    else:

        def __getitem__(self, key):
            return self.environ[key]

        def __setitem__(self, key, value):
            self.environ[key] = value

environ = Environ(os.environ)
