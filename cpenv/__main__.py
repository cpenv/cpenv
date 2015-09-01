# -*- coding: utf-8 -*-
from .vendor import yaml, click
from . import api, scripts
from .shell import ShellScript
from .utils import unipath
import logging

logger = logging.getLogger('cpenv')
# Couple aliases to clarify what's going on
echo = logger.debug
returns = click.echo


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

    scripts.create(name_or_path, config)
    ctx.invoke(activate, name_or_path=name_or_path)


@cli.command()
@click.argument('name_or_path')
def remove(name_or_path):
    '''Remove a virtual environment.'''

    echo('Delete {}? (y/n)'.format(name_or_path))
    do_delete = True if raw_input() == 'y' else False
    if not do_delete:
        return

    echo('Removing environment ' + name_or_path)
    shell_script = scripts.remove(name_or_path)
    returns(shell_script.as_string())


@cli.command()
@click.argument('name_or_path', required=False)
@click.pass_context
def activate(ctx, name_or_path):
    '''Activate a virtual environment.'''

    if not name_or_path:
        ctx.invoke(_list)
        return

    echo('Activating ' + name_or_path)
    shell_script = scripts.activate(name_or_path)
    returns(shell_script.as_string())


@cli.command()
def deactivate():
    '''Deactivate the current environment.'''

    active_env = api.get_active_env()
    if not active_env:
        echo('No active environment...')
        return

    echo('Deactivating ' + active_env)
    shell_script = scripts.deactivate()
    returns(shell_script.as_string())


@cli.command()
@click.argument('name_or_path', required=False)
def upgrade(name_or_path):
    '''Upgrade current environment.'''

    if not name_or_path:
        #do upgrade
        echo('Upgrading packages....')
    elif name_or_path == 'cpenv':

        echo('Upgrading cpenv...')
        shell_script = scripts.upgrade(name_or_path)
        returns(shell_script.as_string())
    else:
        return

@cli.command('list')
def _list():
    '''List available environments'''

    envs = api.get_environments()
    if not envs:
        echo('No available environments...use create to make one:')
        echo('    cpenv create -n <envname>')
    else:
        echo('Available Environments:')
        echo('')
        for e in api.get_environments():
            echo('    ' + e)
        echo('')
        echo('cpenv activate -n <envname>')


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
