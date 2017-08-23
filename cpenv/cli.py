# -*- coding: utf-8 -*-
import os
import collections
from functools import partial
import click
import colorama
import cpenv
import cpenv.utils as utils
import cpenv.shell as shell
from cpenv.cache import EnvironmentCache


red = partial(click.style, fg='red')
green = partial(click.style, fg='green')
blue = partial(click.style, fg='blue')
yellow = partial(click.style, fg='yellow')
cyan = partial(click.style, fg='cyan')
bold_red = partial(click.style, fg='red', bold=True)
bold_green = partial(click.style, fg='green', bold=True)
bold_blue = partial(click.style, fg='blue', bold=True)
bold_yellow = partial(click.style, fg='yellow', bold=True)
bold_cyan = partial(click.style, fg='cyan', bold=True)
bold = partial(click.style, bold=True)


def get_type(obj):
    '''Get the type or classification of an environment or module'''
    # TODO This functionality should be moved to object models

    if isinstance(obj, cpenv.VirtualEnvironment):
        return 'python'

    return 'local' if obj.parent else 'shared'


def _type_and_name(obj):
    '''Sort key for a list of environments and modules'''

    return isinstance(obj, cpenv.Module), obj.name


def contains_env(modules):
    return any([isinstance(m, cpenv.VirtualEnvironment) for m in modules])


def format_object(obj, tmpl):
    '''Format an environment or module for terminal output'''

    return tmpl.format(obj.name, get_type(obj), obj.path)


def format_objects(objects, children=False, columns=None, header=True):
    '''Format a list of environments and modules for terminal output'''

    columns = columns or ('NAME', 'TYPE', 'PATH')
    objects = sorted(objects, key=_type_and_name)
    lines = []
    tmpl = '    {:16}{:16}{:48}'
    local_tmpl = '      {:14}{:16}{:48}'
    if header:
        lines.append('\n' + bold_blue(tmpl.format(*columns)))

    for obj in objects:
        if isinstance(obj, cpenv.VirtualEnvironment):
            lines.append(format_object(obj, tmpl))
            modules = obj.get_modules()
            if children and modules:
                for mod in modules:
                    lines.append(format_object(mod, local_tmpl))
        else:
            lines.append(format_object(obj, tmpl))

    return '\n'.join(lines)


@click.group()
@click.version_option(cpenv.__version__)
def cli():
   '''Cpenv commands'''
   EnvironmentCache.validate()


@cli.command()
def info():
    '''Show context info'''

    env = cpenv.get_active_env()
    modules = []
    if env:
        modules = env.get_modules()
    active_modules = cpenv.get_active_modules()

    if not env and not modules and not active_modules:
        click.echo('\nNo active modules...')
        return

    click.echo(bold('\nActive modules'))
    if env:
        click.echo(format_objects([env] + active_modules))

        available_modules = set(modules) - set(active_modules)
        if available_modules:

            click.echo(
                bold('\nInactive modules in {}\n').format(cyan(env.name))
            )
            click.echo(format_objects(available_modules, header=False))

    else:
        click.echo(format_objects(active_modules))

    available_shared_modules = set(cpenv.get_modules()) - set(active_modules)
    if not available_shared_modules:
        return

    click.echo(bold('\nInactive shared modules \n'))
    click.echo(format_objects(available_shared_modules, header=False))


@cli.command('list')
def list_():
    '''List available environments and modules'''

    environments = cpenv.get_environments()
    modules = cpenv.get_modules()
    click.echo(format_objects(environments + modules, children=True))


@cli.command()
@click.argument('paths', nargs=-1)
@click.option('--skip_local', is_flag=True, help='skip local modules')
@click.option('--skip_shared', is_flag=True, help='skip shared modules')
def activate(paths, skip_local, skip_shared):
    '''Activate an environment'''


    if not paths:
        ctx = click.get_current_context()
        if cpenv.get_active_env():
            ctx.invoke(info)
            return

        click.echo(ctx.get_help())
        examples = (
            '\nExamples: \n'
            '    cpenv activate my_env\n'
            '    cpenv activate ./relative/path/to/my_env\n'
            '    cpenv activate my_env my_module\n'
        )
        click.echo(examples)
        return

    if skip_local:
        cpenv.module_resolvers.remove(cpenv.resolver.module_resolver)
        cpenv.module_resolvers.remove(cpenv.resolver.active_env_module_resolver)

    if skip_shared:
        cpenv.module_resolvers.remove(cpenv.resolver.modules_path_resolver)

    try:
        r = cpenv.resolve(*paths)
    except cpenv.ResolveError as e:
        click.echo('\n' + str(e))
        return

    resolved = set(r.resolved)
    active_modules = set()
    env = cpenv.get_active_env()
    if env:
        active_modules.add(env)
    active_modules.update(cpenv.get_active_modules())

    new_modules = resolved - active_modules
    old_modules = active_modules & resolved

    if old_modules and not new_modules:
        click.echo(
            '\nModules already active: '
            + bold(' '.join([obj.name for obj in old_modules]))
        )
        return

    if env and contains_env(new_modules):
        click.echo('\nUse bold(exit) to leave your active environment first.')
        return

    click.echo('\nResolved the following modules...')
    click.echo(format_objects(r.resolved))
    r.activate()
    click.echo(blue('\nLaunching subshell...'))

    modules = sorted(resolved | active_modules, key=_type_and_name)
    prompt = ':'.join([obj.name for obj in modules])
    shell.launch(prompt)


@cli.command()
@click.argument('name_or_path', required=False)
@click.option('--config', help='Path to config')
def create(name_or_path, config):
    '''Create a new environment.'''

    if not name_or_path:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        examples = (
            '\nExamples:\n'
            '    cpenv create my_env\n'
            '    cpenv create ./relative/path/to/my_env\n'
            '    cpenv create my_env --config ./relative/path/to/config\n'
            '    cpenv create my_env --config git@github.com:user/config.git\n'
        )
        click.echo(examples)
        return

    click.echo(
        blue('Creating a new virtual environment ' + name_or_path)
    )
    try:
        env = cpenv.create(name_or_path, config)
    except Exception as e:
        click.echo(bold_red('FAILED TO CREATE ENVIRONMENT!'))
        click.echo(e)
    else:
        click.echo(bold_green('Successfully created environment!'))
    click.echo(blue('Launching subshell'))

    cpenv.activate(env)
    shell.launch(env.name)


@cli.command()
@click.argument('name_or_path')
def remove(name_or_path):
    '''Remove an environment'''

    click.echo()
    try:
        r = cpenv.resolve(name_or_path)
    except cpenv.ResolveError as e:
        click.echo(e)
        return

    obj = r.resolved[0]
    if not isinstance(obj, cpenv.VirtualEnvironment):
        click.echo('{} is a module. Use `cpenv module remove` instead.')
        return

    click.echo(format_objects([obj]))
    click.echo()

    user_confirmed = click.confirm(
        red('Are you sure you want to remove this environment?')
    )
    if user_confirmed:
        click.echo('Attempting to remove...', nl=False)

        try:
            obj.remove()
        except Exception as e:
            click.echo(bold_red('FAIL'))
            click.echo(e)
        else:
            click.echo(bold_green('OK!'))


@cli.group()
def cache():
    '''Environment cache commands'''


@cache.command('list')
def list_():
    '''List available environments and modules'''

    click.echo('Cached Environments')

    environments = list(EnvironmentCache)
    click.echo(format_objects(environments, children=False))


@cache.command()
@click.argument('path')
def add(path):
    '''Add an environment to the cache. Allows you to activate the environment
    by name instead of by full path'''

    click.echo('\nAdding {} to cache......'.format(path), nl=False)
    try:
        r = cpenv.resolve(path)
    except Exception as e:
        click.echo(bold_red('FAILED'))
        click.echo(e)
        return

    if isinstance(r.resolved[0], cpenv.VirtualEnvironment):
        EnvironmentCache.add(r.resolved[0])
        EnvironmentCache.save()
        click.echo(bold_green('OK!'))


@cache.command()
@click.argument('path')
def remove(path):
    '''Remove a cached environment. Removed paths will no longer be able to
    be activated by name'''

    r = cpenv.resolve(path)
    if isinstance(r.resolved[0], cpenv.VirtualEnvironment):
        EnvironmentCache.discard(r.resolved[0])
        EnvironmentCache.save()


@cache.command()
def clear():
    '''Clear environment cache'''

    if click.confirm('Clear the environment cache?'):
        cpenv.EnvironmentCache.clear()
        click.echo('Cache cleared.')


@cli.group()
def module():
    '''Module commands'''


@module.command()
@click.argument('name_or_path')
@click.option('--config', help='path to config')
def create(name_or_path, config):
    '''Create a new template module.

    You can also specify a filesystem path like "./modules/new_module"
    '''

    click.echo('Creating module {}...'.format(name_or_path), nl=False)
    try:
        module = cpenv.create_module(name_or_path, config)
    except Exception as e:
        click.echo(bold_red('FAILED'))
        raise
    else:
        click.echo(bold_green('OK!'))
        click.echo('Browse to your new module and make some changes.')
        click.echo("When you're ready add the module to an environment:")
        click.echo('    cpenv module add my_module ./path/to/my_module')
        click.echo('Or track your module on git and add it directly from the repo:')
        click.echo('    cpenv module add my_module git@github.com:user/my_module.git')


@module.command()
@click.argument('name', required=False)
@click.argument('path', required=False)
@click.option('--branch', help='Branch to clone if specifying a repo')
@click.option(
    '--type',
    help='local to active environment or shared',
    type=click.Choice(['local', 'shared']),
    default='local',
    show_default=True)
def add(name, path, branch, type):
    '''Add a module to an environment. PATH can be a git repository path or
    a filesystem path. '''

    if not name and not path:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        examples = (
            '\nExamples:\n'
            '    cpenv module add my_module ./path/to/my_module\n'
            '    cpenv module add my_module git@github.com:user/my_module.git'
            '    cpenv module add my_module git@github.com:user/my_module.git --branch=master --type=shared'
        )
        click.echo(examples)
        return

    if not name:
        click.echo('Missing required argument: name')
        return

    if not path:
        click.echo('Missing required argument: path')

    env = cpenv.get_active_env()
    if type=='local':
        if not env:
            click.echo('\nActivate an environment to add a local module.\n')
            return

        if click.confirm('\nAdd {} to active env {}?'.format(name, env.name)):
            click.echo('Adding module...', nl=False)
            try:
                env.add_module(name, path, branch)
            except:
                click.echo(bold_red('FAILED'))
                raise
            else:
                click.echo(bold_green('OK!'))

        return

    module_paths = cpenv.get_module_paths()
    click.echo('\nAvailable module paths:\n')
    for i, mod_path in enumerate(module_paths):
        click.echo('    {}. {}'.format(i, mod_path))
    choice = click.prompt(
        'Where do you want to add your module?',
        type=int,
        default=0
    )
    module_root = module_paths[choice]
    module_path = utils.unipath(module_root, name)
    click.echo('Creating module {}...'.format(module_path), nl=False)
    try:
        cpenv.create_module(module_path, path, branch)
    except:
        click.echo(bold_red('FAILED'))
        raise
    else:
        click.echo(bold_green('OK!'))


@module.command()
@click.argument('name')
@click.option('--local', is_flag=True, help='Ensure we remove a local module')
def remove(name, local):
    '''Remove a module named NAME. Will remove the first resolved module named NAME. You can also specify a full path to a module. Use the --local option
    to ensure removal of modules local to the currently active environment.'''

    click.echo()
    if not local: # Use resolver to find module
        try:
            r = cpenv.resolve(name)
        except cpenv.ResolveError as e:
            click.echo(e)
            return

        obj = r.resolved[0]
    else: # Try to find module in active environment
        env = cpenv.get_active_env()
        if not env:
            click.echo('You must activate an env to remove local modules')
            return

        mod = env.get_module(name)
        if not mod:
            click.echo('Failed to resolve module: ' + name)
            return

        obj = mod

    if isinstance(obj, cpenv.VirtualEnvironment):
        click.echo('{} is an environment. Use `cpenv remove` instead.')
        return

    click.echo(format_objects([obj]))
    click.echo()

    user_confirmed = click.confirm(
        red('Are you sure you want to remove this module?')
    )
    if user_confirmed:
        click.echo('Attempting to remove...', nl=False)

        try:
            obj.remove()
        except Exception as e:
            click.echo(bold_red('FAILED'))
            click.echo(e)
        else:
            click.echo(bold_green('OK!'))


@module.command()
@click.argument('name')
def localize(name):
    '''Copy a global module to the active environment.'''

    env = cpenv.get_active_env()
    if not env:
        click.echo('You need to activate an environment first.')
        return

    try:
        r = cpenv.resolve(name)
    except cpenv.ResolveError as e:
        click.echo('\n' + str(e))

    module = r.resolved[0]
    if isinstance(module, cpenv.VirtualEnvironment):
        click.echo('\nCan only localize a module not an environment')
        return

    active_modules = cpenv.get_active_modules()
    if module in active_modules:
        click.echo('\nCan not localize an active module.')
        return

    if module in env.get_modules():
        click.echo('\n{} is already local to {}'.format(module.name, env.name))
        return

    if click.confirm('\nAdd {} to env {}?'.format(module.name, env.name)):
        click.echo('Adding module...', nl=False)
        try:
            module = env.add_module(module.name, module.path)
        except:
            click.echo(bold_red('FAILED'))
            raise
        else:
            click.echo(bold_green('OK!'))

    click.echo('\nActivate the localize module:')
    click.echo('    cpenv activate {} {}'.format(env.name, module.name))
