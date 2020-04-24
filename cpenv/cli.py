# -*- coding: utf-8 -*-
import os
from functools import partial
import shutil
import click
import cpenv
from cpenv import utils
from cpenv import shell


echo = click.echo
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
        return 'venv'

    return 'module'


def _type_and_name(obj):
    '''Sort key for a list of environments and modules'''

    return isinstance(obj, cpenv.Module), obj.name


def contains_env(modules):
    return any([isinstance(m, cpenv.VirtualEnvironment) for m in modules])


def get_info(obj, indent=0, root=None):

    name = ' ' * indent + obj.name
    type_ = get_type(obj)
    if root:
        path = '...' + os.path.sep + os.path.relpath(obj.path, root)
    else:
        path = obj.path

    return name, type_, path


def format_objects(objects, children=False, columns=None, header=True, indent='', header_color=bold_yellow):
    '''Format a list of environments and modules for terminal output'''

    columns = columns or ('NAME', 'TYPE', 'PATH')
    objects = sorted(objects, key=_type_and_name)
    data = []
    for obj in objects:
        if isinstance(obj, cpenv.VirtualEnvironment):
            data.append(get_info(obj))
            modules = obj.get_modules()
            if children and modules:
                for mod in modules:
                    data.append(get_info(mod, indent=2, root=obj.path))
        else:
            data.append(get_info(obj))

    maxes = [len(max(col, key=len)) for col in zip(*data)]
    tmpl = indent + '{:%d}  {:%d}  {:%d}' % tuple(maxes)
    lines = []
    if header:
        lines.append(header_color(tmpl.format(*columns)))

    for obj_data in data:
        lines.append(tmpl.format(*obj_data))

    return '\n'.join(lines)


@click.group()
@click.version_option(cpenv.__version__)
def cli():
    '''Cpenv commands'''


@cli.command()
def info():
    '''Show context info'''

    ctx = {
        'active_modules': cpenv.get_active_modules(),
        'home_path': cpenv.get_home_path(),
        'modules_path': cpenv.get_module_paths(),
    }
    echo(bold('Context'))
    width = len(max(ctx.keys(), key=len))
    for k, v in ctx.items():
        if not v:
            echo('  {k:>{width}}: {v}'.format(k=k, v=v, width=width))
            continue

        values = []
        if isinstance(v, (list, tuple)):
            for i in range(len(v)):
                v[i] = getattr(v[i], 'name', str(v[i]))
            if len(v) > 1:
                values = v[1:]
            v = v[0]

        echo('  {k:>{width}}: {v}'.format(k=k, v=str(v), width=width))
        for v in values:
            echo('  {k:>{width}}  {v}'.format(k='', v=str(v), width=width))
    echo()

    info = {
        'title': cpenv.__title__,
        'version': cpenv.__version__,
        'license': cpenv.__license__,
        'author': cpenv.__author__,
        'url': cpenv.__url__,
    }
    echo(bold('Package Info'))
    width = len(max(info.keys(), key=len))
    for k, v in info.items():
        echo('  {k:>{width}}: {v}'.format(k=k, v=v, width=width))
    echo()


@cli.command('list')
def list_():
    '''List available environments and modules'''

    modules = cpenv.get_environments() + cpenv.get_modules()

    if not modules:
        echo('No modules found.')
        return

    echo(format_objects(modules, children=True))


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

        echo(ctx.get_help())
        examples = (
            '\nExamples: \n'
            '    cpenv activate my_env\n'
            '    cpenv activate ./relative/path/to/my_env\n'
            '    cpenv activate my_env my_module\n'
        )
        echo(examples)
        return

    if skip_local:
        cpenv.module_resolvers.remove(cpenv.resolver.module_resolver)
        cpenv.module_resolvers.remove(cpenv.resolver.active_env_module_resolver)

    if skip_shared:
        cpenv.module_resolvers.remove(cpenv.resolver.modules_path_resolver)

    try:
        echo('Resolving modules...', nl=False)
        r = cpenv.resolve(*paths)
    except cpenv.ResolveError as e:
        echo(bold_red('FAIL'))
        echo('\n' + bold_red('ResolveError: ') + str(e))
        return

    echo(bold_green('OK!'))

    resolved = set(r.resolved)
    active_modules = set()
    env = cpenv.get_active_env()
    if env:
        active_modules.add(env)
    active_modules.update(cpenv.get_active_modules())

    new_modules = resolved - active_modules
    old_modules = active_modules & resolved

    if old_modules and not new_modules:
        echo('Modules already activated.')
        return

    if env and contains_env(new_modules):
        echo('Use {} to leave your active environment first.')
        return

    echo(format_objects(r.resolved, indent='  '))
    r.activate()
    echo('Activating modules...' + bold_green('OK!'))
    echo('Launching subshell...' + bold_green('OK!'))
    echo()

    modules = sorted(resolved | active_modules, key=_type_and_name)
    prompt = modules[0].name
    if len(modules) > 1:
        prompt += '...'
    shell.launch(prompt)


@cli.command()
@click.argument('name_or_path', required=False)
@click.option('--config', help='Path to config')
def create(name_or_path, config):
    '''Create a new environment.'''

    if not name_or_path:
        ctx = click.get_current_context()
        echo(ctx.get_help())
        examples = (
            '\nExamples:\n'
            '    cpenv create my_env\n'
            '    cpenv create ./relative/path/to/my_env\n'
            '    cpenv create my_env --config ./relative/path/to/config\n'
            '    cpenv create my_env --config git@github.com:user/config.git\n'
        )
        echo(examples)
        return

    echo(
        blue('Creating a new virtual environment ' + name_or_path)
    )
    try:
        env = cpenv.create(name_or_path, config)
    except Exception as e:
        echo(bold_red('FAILED TO CREATE ENVIRONMENT!'))
        echo(e)
    else:
        echo(bold_green('Successfully created environment!'))
    echo(blue('Launching subshell'))

    cpenv.activate(env)
    shell.launch(env.name)


@cli.command()
@click.argument('name_or_path')
def remove(name_or_path):
    '''Remove an environment'''

    echo()
    try:
        r = cpenv.resolve(name_or_path)
    except cpenv.ResolveError as e:
        echo(e)
        return

    obj = r.resolved[0]
    if not isinstance(obj, cpenv.VirtualEnvironment):
        echo('{} is a module. Use `cpenv module remove` instead.')
        return

    echo(format_objects([obj]))
    echo()

    user_confirmed = click.confirm(
        red('Are you sure you want to remove this environment?')
    )
    if user_confirmed:
        echo('Attempting to remove...', nl=False)

        try:
            obj.remove()
        except Exception as e:
            echo(bold_red('FAIL'))
            echo(e)
        else:
            echo(bold_green('OK!'))


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

    echo('Creating module {}...'.format(name_or_path), nl=False)
    try:
        cpenv.create_module(name_or_path, config)
    except Exception:
        echo(bold_red('FAILED'))
        raise
    else:
        echo(bold_green('OK!'))
        echo('Browse to your new module and make some changes.')
        echo("When you're ready add the module to an environment:")
        echo('    cpenv module add my_module ./path/to/my_module')
        echo('Or track your module on git and add it directly from the repo:')
        echo('    cpenv module add my_module git@github.com:user/my_module.git')


@module.command()
@click.argument('name', required=False)
@click.argument('path', required=False)
@click.option('--branch', help='Branch to clone if specifying a repo')
@click.option(
    '--type',
    help='local to active environment or shared',
    type=click.Choice(['local', 'shared']),
    default='shared',
    show_default=True
)
def add(name, path, branch, type):
    '''Add a module to an environment. PATH can be a git repository path or
    a filesystem path. '''

    if not name and not path:
        ctx = click.get_current_context()
        echo(ctx.get_help())
        examples = (
            '\nExamples:\n'
            '    cpenv module add my_module ./path/to/my_module\n'
            '    cpenv module add my_module git@github.com:user/my_module.git'
            '    cpenv module add my_module git@github.com:user/my_module.git --branch=master --type=shared'
        )
        echo(examples)
        return

    if not name:
        echo('Missing required argument: name')
        return

    if not path:
        echo('Missing required argument: path')

    env = cpenv.get_active_env()
    if type == 'local':
        if not env:
            echo('\nActivate an environment to add a local module.\n')
            return

        if click.confirm('\nAdd {} to active env {}?'.format(name, env.name)):
            echo('Adding module...', nl=False)
            try:
                env.add_module(name, path, branch)
            except Exception:
                echo(bold_red('FAILED'))
                raise
            else:
                echo(bold_green('OK!'))

        return

    module_paths = cpenv.get_module_paths()
    echo('\nAvailable module paths:')
    for i, mod_path in enumerate(module_paths):
        echo('    {}. {}'.format(i, mod_path))
    echo()

    choice = click.prompt(
        'Where do you want to add your module?',
        type=int,
        default=0
    )
    echo()

    module_root = module_paths[choice]
    module_path = utils.unipath(module_root, name)
    echo('Checking if module exists...', nl=False)
    if os.path.exists(module_path):
        echo(bold_red('FAIL.'))
        click.confirm(
            'Would you like to overwrite the existing module?',
            abort=True
        )
        shutil.rmtree(module_path)
    else:
        echo(bold_green('OK!'))

    echo('Creating module {}...'.format(module_path), nl=False)
    try:
        cpenv.create_module(module_path, path, branch)
    except Exception:
        echo(bold_red('FAIL.'))
        raise
    else:
        echo(bold_green('OK!'))


@module.command()
@click.argument('name')
@click.option('--local', is_flag=True, help='Ensure we remove a local module')
def remove(name, local):
    '''Remove a module named NAME. Will remove the first resolved module named
    NAME. You can also specify a full path to a module. Use the --local option
    to ensure removal of modules local to the currently active environment.'''

    echo()
    if not local:  # Use resolver to find module
        try:
            r = cpenv.resolve(name)
        except cpenv.ResolveError as e:
            echo(e)
            return

        obj = r.resolved[0]
    else:  # Try to find module in active environment
        env = cpenv.get_active_env()
        if not env:
            echo('You must activate an env to remove local modules')
            return

        mod = env.get_module(name)
        if not mod:
            echo('Failed to resolve module: ' + name)
            return

        obj = mod

    if isinstance(obj, cpenv.VirtualEnvironment):
        echo('{} is an environment. Use `cpenv remove` instead.')
        return

    echo(format_objects([obj]))
    echo()

    user_confirmed = click.confirm(
        red('Are you sure you want to remove this module?')
    )
    if user_confirmed:
        echo('Attempting to remove...', nl=False)

        try:
            obj.remove()
        except Exception as e:
            echo(bold_red('FAILED'))
            echo(e)
        else:
            echo(bold_green('OK!'))


@module.command()
@click.argument('name')
def localize(name):
    '''Copy a global module to the active environment.'''

    env = cpenv.get_active_env()
    if not env:
        echo('You need to activate an environment first.')
        return

    try:
        r = cpenv.resolve(name)
    except cpenv.ResolveError as e:
        echo('\n' + str(e))

    module = r.resolved[0]
    if isinstance(module, cpenv.VirtualEnvironment):
        echo('\nCan only localize a module not an environment')
        return

    active_modules = cpenv.get_active_modules()
    if module in active_modules:
        echo('\nCan not localize an active module.')
        return

    if module in env.get_modules():
        echo('\n{} is already local to {}'.format(module.name, env.name))
        return

    if click.confirm('\nAdd {} to env {}?'.format(module.name, env.name)):
        echo('Adding module...', nl=False)
        try:
            module = env.add_module(module.name, module.path)
        except Exception:
            echo(bold_red('FAILED'))
            raise
        else:
            echo(bold_green('OK!'))

    echo('\nActivate the localized module:')
    echo('    cpenv activate {} {}'.format(env.name, module.name))
