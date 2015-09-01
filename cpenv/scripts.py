import collections
import os
from .vendor import yaml
from .shell import ShellScript
from .utils import unipath
from . import api, platform


def activate(name_or_path):
    '''Generate a shell script to activate a virtual environment that lives
    within your CPENV_HOME path.'''

    env_path = api.get_env_path(name_or_path)

    # Activate for this python process first allows for path expansion
    api.activate(env_path)

    if not os.path.exists(env_path):
        raise EnvironmentError('No Environment: {}'.format(env_path))

    script = ShellScript()

    active_env = api.get_active_env()
    if active_env:
        script.extend(deactivate())

    if not '_CLEAN_ENV' in os.environ:
        store_tmp_path = api.get_store_env_tmp()
        os.environ['_CLEAN_ENV'] = store_tmp_path
        clean_env = api.store_env(store_tmp_path)

        if platform != 'win':
            script.run_cmd('export', 'PS1')

        script.set_env('_CLEAN_ENV', clean_env)

    if platform == 'win':
        script_path = unipath(env_path, 'Scripts', 'activate.bat')
    else:
        script_path = unipath(env_path, 'bin', 'activate')
    script.run_script(script_path)

    wheelhouse = api.get_wheelhouse()
    script.set_env('WHEELHOUSE', wheelhouse)
    script.set_env('PIP_FIND_LINKS', wheelhouse)
    script.set_env('PIP_WHEEL_DIR', wheelhouse)
    script.set_env('ACTIVE_ENV', env_path)

    env_file = unipath(env_path, 'environment.yml')
    if os.path.exists(env_file):
        script.extend(set_env_from_file(env_file))

    return script


def deactivate():
    '''Generate a shell script to activate a virtual environment that lives
    within your CPENV_HOME path.'''

    active_env = api.get_active_env()
    active_env_name = os.path.basename(active_env)

    script = ShellScript()

    if platform == 'win':
        script.run_script(unipath(active_env, 'Scripts', 'deactivate.bat'))
    else:
        script.run_cmd('deactivate')


    clean_env = os.environ.get('_CLEAN_ENV', None)
    if clean_env:
        script.extend(restore_env_from_file(clean_env))

    return script


def create(name_or_path, config=None):
    '''Create an environment in CPENV_HOME directory. Optionally pass
    a yaml configuration file to use in configuring the new environment.

    :param name_or_path: Name or path of the environment to create
    :param config: Config to use for creation
    '''

    env_path = api.create(name_or_path, config)

    return activate(env_path)


def remove(name_or_path):
    '''Remove an environment in CPENV_HOME.'''

    script = ShellScript()

    env_path = api.get_env_path(name_or_path)
    active_env = api.get_active_env()
    if active_env == env_path:
        script.extend(deactivate())

    script.rmtree(env_path)

    return script


def upgrade(name):
    '''Upgrade all packages in an environment, '''
    script = ShellScript()

    active_env = api.get_active_env()
    if active_env:
        script.extend(deactivate())

    if name == 'cpenv':
        script.run_cmd('pip', 'install', '--upgrade', name)

    return script


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
