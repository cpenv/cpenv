# -*- coding: utf-8 -*-

from .packages import click
from . import api, shell
from .cache import EnvironmentCache
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
            echo('    [{}] {}'.format(env.name, env.path))
        echo('')
        echo('cpenv activate <name_or_path>')


def list_modules():
    '''List available application modules'''

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
    echo('')
    echo('You can pass arguments by separating the module_name and args with --')
    echo('')
    echo('cpenv launch <module_name> -- <args>')


@click.group()
def cli():
    '''Python Environment Management'''


@cli.command()
@click.argument('name_or_path', required=True)
@click.argument('module_repo', required=False)
@click.option('--module', required=False, is_flag=True, default=False)
@click.option('--config', required=False)
def create(name_or_path, module_repo, module, config):
    '''Create a new virtual environment'''

    if module:

        if not module_repo:
            echo('Pass the path to a repo when creating an app module')
            echo('cpenv create --module maya2016 '
                 'https://git@github.com/cpenv/maya_module.git')

        active_env = api.get_active_env()
        if not active_env:
            echo('No active environment...')
            return

        active_env.add_module(name_or_path, module_repo)
        return

    echo('Creating new environment ' + name_or_path)
    if config:
        echo('Using configuration ' + config)

    env = api.create(name_or_path, config=config)

    echo('Activating ' + env.name)
    api.activate(env)
    sys.exit(shell.launch(prompt_prefix=env.name))


@cli.command()
@click.option('--config', required=False, type=click.Path(exists=True))
def update(config):
    '''Update a virtual environment'''

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
    '''Remove a virtual environment'''

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

    if not click.confirm('Delete {}?'.format(env.path)):
        return

    echo('Removing environment ' + env.path)
    env.remove()


@cli.command()
@click.argument('paths', nargs=-1, required=False)
def activate(paths):
    '''Activate a virtual environment'''

    if not paths:
        list_environments()
        return

    echo('Activating ' + ' '.join(paths))
    env = api.activate(*paths)
    names = []
    if env:
        names.append(env.name)
    modules = [m.name for m in api.get_active_modules()]
    names.extend(modules)
    prompt_prefix = ':'.join(names)
    sys.exit(shell.launch(prompt_prefix=prompt_prefix))


@cli.command()
def clear_cache():
    '''Clean environment cache'''

    echo('Any paths not in CPENV_HOME will no longer be callable by name.')
    if click.confirm('Clear environment path cache?'):
        EnvironmentCache.clear()
        EnvironmentCache.save()
    return


@cli.command()
@click.argument('module_name', required=False)
@click.argument('args', nargs=-1, required=False)
def launch(module_name, args):
    '''Launch an application module'''

    if not module_name:
        list_modules()
        return

    active_env = api.get_active_env()
    if not active_env:
        echo('You must activate an environment first...')
        return

    try:
        api.launch(module_name, *args)
        return
    except NameError:
        pass

    echo('Application module named {} does not exist...'.format(module_name))
    list_modules()


if __name__ == "__main__":
    cli()
