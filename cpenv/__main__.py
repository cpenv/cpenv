# -*- coding: utf-8 -*-

from .packages import yaml, click
from . import api, shell
from .util import unipath, is_system_path
import shutil
import sys
import logging

logger = logging.getLogger('cpenv')
echo = click.echo


def list_environments():
    '''List available environments'''

    envs = api.get_environments()
    if not envs:
        echo('No available environments...use create to make one:')
        echo('    cpenv create <name_or_path>')
    else:
        echo('Available Environments:')
        echo('')
        for env in envs:
            echo('    [{}] {}'.format(env.name, env.root))
        echo('')
        echo('cpenv activate <name_or_path>')


def list_modules():
    '''List available application modules.'''

    active_env = api.get_active_env()
    if not active_env:
        echo('You must activate an environment first...')
        return

    echo('Available Application Modules:')
    echo('')
    for mod in active_env.get_modules():
        echo('    [{}] {}'.format(mod.name, mod.command))
    echo('')
    echo('cpenv launch <module_name>')


@click.group()
def cli():
    '''Python Environment Management'''


@cli.command()
@click.argument('name_or_path', required=True)
@click.argument('module_repo', required=False)
@click.option('--module', required=False, is_flag=True, default=False)
@click.option('--config', required=False, type=click.Path(exists=True))
def create(name_or_path, module_repo, module, config):
    '''Create a new virtual environment.'''

    if module:

        if not module_repo:
            echo('Pass the path to a repo when creating an app module')
            echo('cpenv create --module maya2016 https://git@github.com/cpenv/maya_module.git')

        active_env = api.get_active_env()
        if not active_env:
            echo('No active environment...')
            return

        active_env.add_module(name_or_path, module_repo)
        return

    echo('Creating new environment ' + name_or_path)
    if config:
        config = unipath(config)
        echo('Using configuration ' + config)

    env = api.create(name_or_path, config=config)

    echo('Activating ' + env.name)
    env.activate()
    sys.exit(shell.launch(prompt_prefix=env.name))


@cli.command()
@click.option('--config', required=False, type=click.Path(exists=True))
def update(config):
    '''Update a virtual environment.'''

    active_env = api.get_active_env()
    if not active_env:
        echo('You must activate an environment first...')
        return

    echo('Updating ' + active_env.name)
    active_env.update(config)


@cli.command()
@click.argument('name_or_path', required=False)
@click.option('--module', required=False, is_flag=True, default=False)
def remove(name_or_path, module):
    '''Remove a virtual environment.'''

    if not name_or_path and not module:
        list_environments()
        return

    if not name_or_path and module:
        list_modules()
        return

    if module:

        active_env = api.get_active_env()
        if not active_env:
            echo('No active environment...')
            return

        active_env.rem_module(name_or_path)
        return

    try:
        env = api.get_environment(name_or_path)
    except NameError:
        echo('No environment matches {}...'.format(name_or_path))
        list_environments()
        return

    echo('Delete {}? (y/n)'.format(env.root))
    do_delete = True if raw_input() == 'y' else False
    if not do_delete:
        return

    echo('Removing environment ' + env.root)
    env.remove()


@cli.command()
@click.argument('name_or_path', required=False)
@click.option('--clear_cache', help='Clear path cache.', required=False,
              is_flag=True, default=False)
def activate(name_or_path, clear_cache):
    '''Activate a virtual environment.'''

    if clear_cache:
        echo('Clear environment path cache? (y/n)')
        echo('Any paths not in CPENV_HOME will no longer be callable by name.')
        do_clear = True if raw_input() == 'y' else False
        if do_clear:
            api.CACHE.clear()
            api.CACHE.save()
        return

    if not name_or_path:
        list_environments()
        return

    try:
        env = api.get_environment(name_or_path)
    except NameError:
        echo('No environment matches {}...'.format(name_or_path))
        list_environments()
        return

    echo('Activating ' + env.name)
    env.activate()
    sys.exit(shell.launch(prompt_prefix=env.name))


@cli.command()
@click.argument('module_name', required=False)
def launch(module_name):
    '''Launch an application module'''

    if not module_name:
        list_modules()
        return

    active_env = api.get_active_env()
    if not active_env:
        echo('You must activate an environment first...')
        return

    modules = active_env.get_modules()
    for mod in modules:
        if mod.name == module_name:
            mod.launch()
            return

    echo('Application module named {} does not exist...'.format(module_name))
    list_modules()


if __name__ == "__main__":
    cli()
