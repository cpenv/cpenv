# -*- coding: utf-8 -*-

import os
import random
import shlex
import shutil
import stat
import sys
import tempfile
from string import Template
from .packages import yaml
from . import platform
from .compat import string_types, numeric_types


def is_git_repo(path):
    '''Returns True if path is a git repository.'''

    if path.startswith('git@') or path.startswith('https://'):
        return True

    if os.path.exists(unipath(path, '.git')):
        return True

    return False


def is_home_environment(path):
    '''Returns True if path is in CPENV_HOME'''

    home = unipath(os.environ.get('CPENV_HOME', '~/.cpenv'))
    path = unipath(path)

    return path.startswith(home)


def is_environment(path):
    '''Returns True if path refers to an environment'''

    return os.path.exists(unipath(path, 'environment.yml'))


def is_module(path):
    '''Returns True if path refers to a module'''

    return os.path.exists(unipath(path, 'module.yml'))


def is_system_path(path):
    '''Returns True if path is a system path'''

    return '\\' in path or '/' in path


def is_redirecting(path):
    '''Returns True if path contains a .cpenv file'''

    candidate = unipath(path, '.cpenv')
    return os.path.exists(candidate) and os.path.isfile(candidate)


def redirect_to_env_paths(path):
    '''Get environment path from redirect file'''

    with open(path, 'r') as f:
        data = f.read()

    return parse_redirect(data)


def parse_redirect(data):
    '''Parses a redirect string - data of a .cpenv file'''

    lines = [line for line in data.split('\n') if line]
    if len(lines) == 1:
        return shlex.split(lines[0])
    else:
        return lines



def expandpath(path):
    '''Returns an absolute expanded path'''

    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


def unipath(*paths):
    '''Like os.path.join but also expands and normalizes path parts.'''

    return os.path.normpath(expandpath(os.path.join(*paths)))


def binpath(*paths):
    '''Like os.path.join but acts relative to this packages bin path.'''

    package_root = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(package_root, 'bin', *paths))


def ensure_path_exists(path, *args):
    '''Like os.makedirs but keeps quiet if path already exists'''
    if os.path.exists(path):
        return

    os.makedirs(path, *args)


def walk_dn(start_dir, depth=10):
    '''
    Walk down a directory tree. Same as os.walk but allows for a depth limit
    via depth argument
    '''

    start_depth = len(os.path.split(start_dir))
    end_depth = start_depth + depth

    for root, subdirs, files in os.walk(start_dir):
        yield root, subdirs, files

        if len(os.path.split(root)) >= end_depth:
            break


def rmtree(path):
    def onerror(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(path, onerror=onerror)


def walk_up(start_dir, depth=20):
    '''
    Walk up a directory tree
    '''
    root = start_dir

    for i in xrange(depth):
        contents = os.listdir(root)
        subdirs, files = [], []
        for f in contents:
            if os.path.isdir(os.path.join(root, f)):
                subdirs.append(f)
            else:
                files.append(f)

        yield root, subdirs, files

        parent = os.path.dirname(root)
        if parent and not parent == root:
            root = parent
        else:
            break


def touch(filepath):
    '''Touch the given filepath'''

    with open(filepath, 'a'):
        os.utime(filepath, None)


def _pre_dict(d):

    value = d.get(platform)
    value = PREPROCESSORS[type(value)](value)
    return value


def _pre_seq(seq):
    value = []
    for item in seq:
        item_value = PREPROCESSORS[type(item)](item)
        if isinstance(item_value, (list, tuple, set)):
            value.extend(item_value)
        else:
            value.append(item_value)
    return value


def _pre_str(s):
    return str(s)


PREPROCESSORS = {
    dict: _pre_dict,
    list: _pre_seq,
    set: _pre_seq,
    tuple: _pre_seq,
}

PREPROCESSORS.update(
    dict((typ, _pre_str) for typ in numeric_types + string_types)
)


def preprocess_dict(d):
    '''
    Preprocess a dict to be used as environment variables.

    :param d: dict to be processed
    '''

    out_env = {}
    for k, v in d.items():

        if not type(v) in PREPROCESSORS:
            raise KeyError('Invalid type in dict: {}'.format(type(v)))

        out_env[k] = PREPROCESSORS[type(v)](v)

    return out_env


def _join_dict(d, k, v):
    '''Add a dict value to an env dict'''

    d[k] = v[platform]


def _join_str(d, k, v):
    '''Add a string value to env dict'''

    d[k] = str(v)


def _join_seq(d, k, v):
    '''Add a sequence value to env dict'''

    if k not in d:
        d[k] = list(v)

    elif isinstance(d[k], list):
        for item in v:
            if item not in d[k]:
                d[k].insert(0, item)

    elif isinstance(d[k], string_types):
        v.append(d[k])
        d[k] = v


JOINERS = {
    dict: _join_dict,
    list: _join_seq,
    set: _join_seq,
    tuple: _join_seq,
}

JOINERS.update(
    dict((typ, _join_str) for typ in numeric_types + string_types)
)


def join_dicts(*dicts):
    '''Join a bunch of dicts'''

    out_dict = {}

    for d in dicts:
        for k, v in d.iteritems():

            if not type(v) in JOINERS:
                raise KeyError('Invalid type in dict: {}'.format(type(v)))

            JOINERS[type(v)](out_dict, k, v)

    return out_dict


def env_to_dict(env, pathsep=os.pathsep):
    '''
    Convert a dict containing environment variables into a standard dict.
    Variables containing multiple values will be split into a list based on
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


def dict_to_env(d, pathsep=os.pathsep):
    '''
    Convert a python dict to a dict containing valid environment variable
    values.

    :param d: Dict to convert to an env dict
    :param pathsep: Path separator used to join lists(default os.pathsep)
    '''

    out_env = {}

    for k, v in d.iteritems():
        if isinstance(v, list):
            out_env[k] = pathsep.join(v)
        elif isinstance(v, string_types):
            out_env[k] = v
        else:
            raise TypeError('{} not a valid env var type'.format(type(v)))

    return out_env


def expand_envvars(env):
    '''
    Expand all environment variables in an environment dict

    :param env: Environment dict
    '''

    out_env = {}

    for k, v in env.iteritems():
        out_env[k] = Template(v).safe_substitute(env)

    # Expand twice to make sure we expand everything we possibly can
    for k, v in out_env.items():
        out_env[k] = Template(v).safe_substitute(out_env)

    return out_env


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

    replace_osenviron(expand_envvars(dict_to_env(env_dict)))


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
    new_env_dict = join_dicts(old_env_dict, *env_dicts)
    new_env = dict_to_env(new_env_dict)
    replace_osenviron(expand_envvars(new_env))


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
        if k not in env_dict:
            del os.environ[k]

    for k, v in env_dict.iteritems():
        os.environ[k] = v
