# -*- coding: utf-8 -*-
from .vendor import yaml, click
from . import api
from .shell import ShellScript
from .utils import unipath
import logging

logger = logging.getLogger('cpenv')
# Couple aliases to clarify what's going on
echo = logger.debug
returns = click.echo


def is_path(input_str):
    return '\\' in input_str or '/' in input_str


def get_environments(name_or_path):
    if is_path(name_or_path):
        return api.get_environments(root=name_or_path)
    else:
        return api.get_environments(name=name_or_path)


@click.group()
def cli():
    '''Python Environment Management'''


@cli.command()
@click.argument('name_or_path', required=True)
@click.option('--config', '-c', required=False, type=click.Path(exists=True))
@click.pass_context
def create(ctx, name_or_path, config):
    '''Create a new virtual environment.'''

    echo('Creating new environment ' + name_or_path)
    if config:
        config = unipath(config)
        echo('Using configuration ' + config)

    if is_path(name_or_path):
        env = api.create_environment(root=name_or_path, config=config)
    else:
        env = api.create_environment(name=name_or_path, config=config)

    returns(env.activate_script().as_string())


@cli.command()
@click.argument('name_or_path')
def remove(name_or_path):
    '''Remove a virtual environment.'''

    envs = get_environments(name_or_path)

    if len(envs) > 1:
        echo('More then one environment matches {}...'.format(envs[0].name))
        ctx.invoke(_list)
        return

    env = envs[0]
    echo('Delete {}? (y/n)'.format(env.root))
    do_delete = True if raw_input() == 'y' else False
    if not do_delete:
        return

    echo('Removing environment ' + env.root)
    env.remove()


@cli.command()
@click.argument('name_or_path', required=False)
@click.pass_context
def activate(ctx, name_or_path):
    '''Activate a virtual environment.'''

    if not name_or_path:
        ctx.invoke(_list)
        return

    envs = get_environments(name_or_path)

    if len(envs) > 1:
        echo('More then one environment matches {}...'.format(envs[0].name))
        ctx.invoke(_list)
        return

    env = envs[0]
    echo('Activating ' + env.name)
    returns(env.activate_script().as_string())


@cli.command()
def deactivate():
    '''Deactivate the current environment.'''

    active_env = api.get_active_env()
    if not active_env:
        echo('No active environment...')
        return

    returns(api.deactivate_script().as_string())


@cli.command()
@click.argument('name_or_path', required=False)
def upgrade(name_or_path):
    '''Upgrade current environment.'''

    return


@cli.command('list')
def _list():
    '''List available environments'''

    envs = api.get_environments()
    if not envs:
        echo('No available environments...use create to make one:')
        echo('    cpenv create <name_or_path>')
    else:
        echo('Available Environments:')
        echo('')
        for env in envs:
            echo('    {}> {}'.format(env.name, env.root))
        echo('')
        echo('cpenv activate <name_or_path>')


@cli.command('list_apps')
def list_apps():
    '''List available application modules.'''

    active_env = api.get_active_env()
    if not active_env:
        echo('You must activate an environment first...')
        return

    echo('Available Application Modules:')
    echo('')
    for app in active_env.get_application_modules():
        echo('    {}> {}'.format(app.name, app.root))
    echo('')
    echo('cpenv launch <module_name>')


@cli.command()
@click.argument('module_name', required=False)
@click.pass_context
def launch(ctx, module_name):
    '''Launch an application module'''

    if not module_name:
        ctx.invoke(list_apps)
        return

    active_env = api.get_active_env()
    if not active_env:
        echo('You must activate an environment first...')
        return

    modules = active_env.get_application_modules()
    for mod in modules:
        if mod.name == module_name:
            mod.launch()
            return

    echo('Application module named {} does not exist...'.format(module_name))
    ctx.invoke(list_apps)


@cli.command()
@click.option('--filepath', '-f', required=False)
def store(filepath):
    '''Store the current environment in a yaml file.'''

    if filepath:
        filepath = unipath(filepath)

    store_filepath = api.store_env(filepath)
    echo('Environment stored in ' + store_filepath)

    returns(store_filepath)


@cli.command('set')
@click.option('--filepath', '-f',
              help='Path to env yaml file',
              required=False,
              type=click.Path(exists=True))
@click.option('--variable', '-v', multiple=True, required=False)
@click.pass_context
def _set(ctx, filepath, variable):
    '''Set an environment from a yaml environment file.'''


    if not filepath and not variable:
        returns(ctx.get_help())
        return
    elif not filepath:
        shell_script = scripts.ShellScript()
    else:
        filepath = unipath(filepath)
        shell_script = scripts.set_env_from_file(filepath)

    echo('Setting up environment using: ' + filepath)
    for var in variable:
        if not '=' in var:
            raise ValueError(
                'Variables set with the -v argument must use the following '
                'syntax:\n'
                '-v PATH=["A/Path/To/Pass"]')
        name, value = var.split('=')
        value = eval(value)
        echo('Setting additional envvar: {}={}'.format(name, value))
        shell_script.set_env(name, value)

    returns(shell_script.as_string())


@cli.command()
@click.option('--filepath', '-f',
              help='Path to env yaml file',
              required=True,
              type=click.Path(exists=True))
def restore(filepath):
    '''Restore an environment from a yaml environment file.

    restore differs from set in that restore will unset variables not defined
    in the yaml environment file.'''

    filepath = unipath(filepath)
    echo('Restoring environment from ' + filepath)

    shell_script = scripts.restore_env_from_file(filepath)
    returns(shell_script.as_string())


if __name__ == "__main__":
    cli()
