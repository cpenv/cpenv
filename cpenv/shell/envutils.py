import collections
import os
from .shell import ShellScript
from ..vendor import yaml
from ..utils import unipath
from .. import platform


def format_envvar(var, value):

    if isinstance(value, basestring):
        return str(unipath(value))
    if isinstance(value, collections.Sequence):
        paths = [unipath(path) for path in value]
        old_value = os.environ.get(var, None)
        if old_value:
            old_paths = old_value.split(os.pathsep)
            for path in old_paths:
                if not path in paths:
                    paths.append(path)
        return str(os.pathsep.join(paths))
    if isinstance(value, (int, long, float)):
        return str(value)
    if isinstance(value, dict):
        if platform in value:
            return format_envvar(var, value[platform])
        else:
            raise EnvironmentError(
                "Failed to set {}={}\n <type 'dict'> values must include "
                "platforms win, linux, osx".format(var, value))
    else:
        typ = type(value)
        raise EnvironmentError(
            'Environment variables must be sequences, strings or numbers.\n'
            'Received type: {} for var {}'.format(typ, var))


def set_env(**env_dict):
    '''Generate a shell script to set environment variables from a dictionary
    containing envvars and values.'''

    script = ShellScript()

    for k, v in env_dict.iteritems():
        script.set_env(k, format_envvar(k, v))

    return script


def set_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.load(f.read())

    return set_env(**env_dict)


def restore_env(**env_dict):
    '''Generate a shell script to restore an environment from a dictionary
    containing envvars and values.'''

    script = ShellScript()

    unset_variables = set(os.environ.keys()) - set(env_dict.keys())
    for envvar in unset_variables:
        script.unset_env(envvar)

    for k, v in env_dict.iteritems():
        script.set_env(k, format_envvar(k, v))

    return script


def restore_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.load(f.read())

    return restore_env(**env_dict)
