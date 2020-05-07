# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import argparse
import os
import re
import sys

# Local imports
import cpenv
from cpenv import (
    LocalRepo,
    Resolver,
    Copier,
    ResolveError,
    api,
    cli,
    shell,
    utils,
)
from cpenv.module import (
    parse_module_path,
    is_partial_match,
    best_match,
    sort_modules,
)


class CpenvCLI(cli.CLI):
    '''
    Create, activate and manage Modules.

    A Module is a folder containing a module.yml file describing the Module's
    name, version, requirements, and environment variables. Module's can also
    contain a hooks folder with python files that respond to specific events.
    '''

    name = 'cpenv'
    usage = 'cpenv [-h] <command> [<args>...]'

    def commands(self):
        return [
            Activate(self),
            Clone(self),
            Copy(self),
            Create(self),
            Info(self),
            List(self),
            Localize(self),
            Publish(self),
            Remove(self),
            Repo(self),
            Version(self),
        ]


class Info(cli.CLI):
    '''Show Module info'''

    usage = 'cpenv info [-h] [<modules>...]'

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='+',
        )

    def run(self, args):
        cli.echo()
        cli.echo('- Resolving modules...', end='')
        try:
            module_specs = api.resolve(args.modules)
        except ResolveError:
            cli.echo('OOPS!')
            cli.echo()
            cli.echo('Error: failed to resolve %s' % args.modules)
            sys.exit(1)
        cli.echo('OK!')

        cli.echo()
        for spec in module_specs:
            cli.echo(cli.format_section(
                spec.real_name,
                [(k, str(v)) for k, v in sorted(spec._asdict().items())]
            ))
            cli.echo()


class Activate(cli.CLI):
    '''Activate a list of Modules.'''

    usage = 'cpenv activate [-h] [<modules>...]'

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='+',
        )

    def run(self, args):
        cli.echo()
        cli.echo('- Resolving modules...', end='')
        try:
            activated_modules = api.activate(args.modules)
        except ResolveError:
            cli.echo('OOPS!')
            cli.echo()
            cli.echo('Error: failed to resolve %s' % args.modules)
            sys.exit(1)
        cli.echo('OK!')

        cli.echo()
        for module in activated_modules:
            cli.echo('  ' + module.real_name)
        cli.echo()

        cli.echo('- Launching subshell...')
        cli.echo()
        shell.launch('[*]')


class Clone(cli.CLI):
    '''
    Clone a Module for development.

    The following repos are available by default:
        home - Local repo pointing to a computer-wide cpenv directory
        user - Local repo pointing to a user-specific cpenv directory

    For a full listing of available repos use the repo cli command:
        cpenv repo list
    '''

    def setup_parser(self, parser):
        parser.add_argument(
            'module',
            help='Module to clone.',
        )
        parser.add_argument(
            'where',
            help='Destination directory. (./<module_name>)',
            nargs='?',
            default=None,
        )
        parser.add_argument(
            '--from_repo',
            help='Specific repo to clone from.',
            default=None,
        )
        parser.add_argument(
            '--overwrite',
            help='Overwrite the destination directory. (False)',
            action='store_true',
        )

    def run(self, args):

        cli.echo('- Cloning %s...' % args.module, end='')
        try:
            module = api.clone(
                args.module,
                args.from_repo,
                args.where,
                args.overwrite,
            )
        except Exception as e:
            cli.echo()
            cli.echo('Error: ' + str(e))
            sys.exit(1)

        cli.echo('OK!')
        cli.echo()
        cli.echo('Navigate to the following folder to make changes:')
        cli.echo('  ' + module.path)
        cli.echo()
        cli.echo("Use one of the following commands to publish your changes:")
        cli.echo('  cpenv publish .')
        cli.echo('  cpenv publish . --to_repo="repo_name"')


class Create(cli.CLI):
    '''Create a new Module.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'where',
            help='Path to new module',
        )
        parser.add_argument(
            '--name',
            help='Name of new module',
            default='',
        )
        parser.add_argument(
            '--version',
            help='Version of the new module',
            default='',
        )
        parser.add_argument(
            '--description',
            help='Details about the module',
            default='',
        )
        parser.add_argument(
            '--author',
            help='Author of the module',
            default='',
        )
        parser.add_argument(
            '--email',
            help="Author's email address",
            default='',
        )

    def run(self, args):
        cli.echo()
        where = utils.normpath(args.where)
        name, version = parse_module_path(where)

        cli.echo('- Creating a Module...', end='')
        module = api.create(
            where=where,
            name=args.name or name,
            version=args.version or version.string,
            description=args.description,
            author=args.author,
            email=args.email,
        )
        cli.echo('OK!')

        cli.echo()
        cli.echo('  name     ' + module.name)
        cli.echo('  version  ' + module.version.string)
        cli.echo('  path     ' + module.path)
        cli.echo()

        cli.echo('Some steps you might take before publishing...')
        cli.echo()
        cli.echo('  - Include binaries your module depends on')
        cli.echo('  - Edit the module.yml file')
        cli.echo('    - Add variables to the environment section')
        cli.echo('    - Add other modules to the requires section')
        cli.echo('  - Add python hooks like post_activate')


class List(cli.CLI):
    '''List active and available Modules.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'requirement',
            help='Space separated list of modules.',
            nargs='?',
            default=None,
        )
        parser.add_argument(
            '--verbose', '-v',
            help='Print more module info.',
            action='store_true',
        )

    def run(self, args):

        found_modules = False

        cli.echo()
        active_modules = api.get_active_modules()
        if args.requirement:
            active_modules = [
                m for m in active_modules
                if is_partial_match(args.requirement, m)
            ]

        if active_modules:
            found_modules = True
            cli.echo(cli.format_columns(
                '[*] Active',
                [m.real_name for m in sort_modules(active_modules)],
            ))
            cli.echo()

        for repo in api.get_repos():
            if args.requirement:
                repo_modules = repo.find(args.requirement)
            else:
                repo_modules = repo.list()

            module_names = []
            for module in sort_modules(repo_modules):
                if module in active_modules:
                    module_names.append('* ' + module.real_name)
                else:
                    module_names.append('  ' + module.real_name)

            if module_names:
                found_modules = True
                if repo.name != repo.path:
                    header = repo.name + ' - ' + repo.path
                else:
                    header = repo.name
                cli.echo(cli.format_columns(
                    '[ ] ' + header,
                    module_names,
                    indent='  ',
                ))
                cli.echo()

        if not found_modules:
            cli.echo('No modules are available.')


class Localize(cli.CLI):
    '''Localize a list of Modules.

    Downloads modules from a remote Repo and places them in the home LocalRepo
    by default. Use the --to_repo option to specify a LocalRepo.
    '''

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='+',
        )
        parser.add_argument(
            '--to_repo', '-r',
            help='Specific repo to localize to. (first match)',
            default=None,
        )
        parser.add_argument(
            '--overwrite', '-o',
            help='Overwrite the destination directory. (False)',
            action='store_true',
        )

    def run(self, args):

        cli.echo()

        if args.to_repo:
            to_repo = api.get_repo(name=args.to_repo)
        else:
            repos = [r for r in api.get_repos() if isinstance(r, LocalRepo)]
            to_repo = prompt_for_repo(
                repos,
                'Choose a repo to localize to',
                default_repo_name='home',
            )

        cli.echo()
        cli.echo(
            '- Localizing %s to %s...' % (args.modules, to_repo.name),
            end='',
        )
        modules = api.localize(
            args.modules,
            to_repo=to_repo,
            overwrite=args.overwrite,
        )
        cli.echo('OK!')
        cli.echo()

        cli.echo()
        cli.echo('Localized the following modules:')
        for module in modules:
            cli.echo('  %s - %s' % (module.real_name, module.path))


class Copy(cli.CLI):
    '''Copy Modules from one Repo to another.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='+',
        )
        parser.add_argument(
            '--from_repo',
            help='Download from',
            default=None,
        )
        parser.add_argument(
            '--to_repo',
            help='Upload to',
            default=None,
        )
        parser.add_argument(
            '--overwrite',
            help='Overwrite the destination directory. (False)',
            action='store_true',
        )

    def run(self, args):

        cli.echo()

        if args.from_repo:
            from_repo = api.get_repo(args.from_repo)
        else:
            from_repo = prompt_for_repo(
                api.get_repos(),
                'Download from',
                default_repo_name='home',
            )
            cli.echo()

        if args.to_repo:
            to_repo = api.get_repo(args.to_repo)
        else:
            to_repo = prompt_for_repo(
                api.get_repos(),
                'Upload to',
                default_repo_name='home',
            )
            cli.echo()

        cli.echo('- Resolving modules from %s...' % from_repo.name, end='')
        resolver = Resolver([from_repo])
        module_specs = resolver.resolve(args.modules)
        cli.echo('OK!')
        cli.echo()
        for module_spec in module_specs:
            cli.echo('  %s - %s' % (module_spec.real_name, module_spec.path))
        cli.echo()

        choice = cli.prompt('Copy these modules to %s?(y/n)' % to_repo.name)
        if choice.lower() not in ['y', 'yes', 'yup']:
            cli.echo('Aborted.')
            sys.exit(1)
        cli.echo()

        copier = Copier(to_repo)
        for module_spec in module_specs:
            cli.echo('- Copying %s...' % module_spec.real_name, end='')
            copier.copy([module_spec], args.overwrite)
            cli.echo('OK!')


class Publish(cli.CLI):
    '''Publish a Module to a repo.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'module',
            help='Path of module to publish. (".")',
            default='.',
            nargs='?',
        )
        parser.add_argument(
            '--to_repo',
            help='Specific repo to clone from.',
            default=None,
        )
        parser.add_argument(
            '--overwrite',
            help='Overwrite the destination directory. (False)',
            action='store_true',
        )

    def run(self, args):

        cli.echo()

        if args.to_repo:
            to_repo = api.get_repo(name=args.to_repo)
        else:
            to_repo = prompt_for_repo(
                api.get_repos(),
                'Choose a repo to publish to',
                default_repo_name='home',
            )

        cli.echo()
        cli.echo(
            '- Publishing %s to %s...' % (args.module, to_repo.name),
            end='',
        )
        module = api.publish(args.module, to_repo, args.overwrite)
        cli.echo('OK!', end='\n\n')

        cli.echo('Activate it using the following command:')
        cli.echo('  cpenv activate %s' % module.real_name)


class Remove(cli.CLI):
    '''Permanently remove a Module from a Repo.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'module',
            help='Module to remove.',
        )
        parser.add_argument(
            '--from_repo',
            help='Specific repo to remove from.',
            default=None,
        )
        parser.add_argument(
            '--quiet',
            help='Overwrite the destination directory. (False)',
            action='store_true',
        )

    def run(self, args):

        cli.echo()

        if args.from_repo:
            from_repo = api.get_repo(name=args.from_repo)
        else:
            from_repo = prompt_for_repo(
                api.get_repos(),
                'Choose a repo to remove module from',
                default_repo_name='home',
            )

        cli.echo(
            '- Finding module %s in %s...' % (args.module, from_repo.name),
            end='',
        )
        module = best_match(args.module, from_repo.find(args.module))
        if not module:
            cli.echo('OOPS!', end='\n\n')
            cli.echo(
                'Error: %s not found in %s' % (args.module, from_repo.name)
            )
            sys.exit(1)
        cli.echo('OK!')

        cli.echo()
        cli.echo('%s - %s' % (module.name, module.path))
        cli.echo()

        choice = cli.prompt('Delete this module?(y/n)')
        if choice.lower() not in ['y', 'yes', 'yup']:
            cli.echo('Aborted.')
            sys.exit(1)

        cli.echo()
        cli.echo('- Removing module...', end='')
        api.remove(module, from_repo)
        cli.echo('OK!', end='\n\n')

        cli.echo('Successfully removed module.')


class Repo(cli.CLI):
    '''
    Manage, Configure and list Repos.

    Repos are sources of Modules. A Repo can be local or remote. Modules
    stored in remote Repos will be localized to a local repo prior to
    activation or explicitly by using "cpenv localize".
    '''

    def commands(self):
        return [
            ListRepo(self),
            AddRepo(self),
            RemoveRepo(self),
        ]


class ListRepo(cli.CLI):
    '''List configured repos'''

    name = 'list'

    def run(self, args):

        cli.echo()
        cli.echo('Repos in order of resolution:')
        for i, repo in enumerate(api.get_repos()):
            if repo.path == repo.name:
                cli.echo('  [{}] {}  {}'.format(
                    i,
                    type(repo).__name__,
                    repo.path,
                ))
            else:
                cli.echo('  [{}] {}  {}  {}'.format(
                    i,
                    type(repo).__name__,
                    repo.name,
                    repo.path,
                ))


class AddRepo(cli.CLI):
    '''Add a new repo.

    LocalRepo:
        cpenv repo add custom --path=~/custom_repo

    ShotgunRepo:
        cpenv repo add my_shotgun --type=shotgun --base_url=https://my.shotgunstudio.com --script_name=cpenv --api_key=secret
    '''

    name = 'add'

    def setup_parser(self, parser):
        parser.add_argument(
            '--type',
            help='Type of repo',
            choices=['local', 'shotgun'],
            default='local',
        )
        parser.add_argument(
            'name',
            help='Name of the repo',
        )
        parser.add_argument(
            'type_args',
            help='Type specific arguments.',
            nargs=argparse.REMAINDER,
        )

    def parse_type_args(self, type_args):
        pattern = (
            r'-{1,2}(?P<param>[a-zA-Z0-9_]+)=*\s*'
            r'"?(?P<value>.+)"?'
        )
        kwargs = {}
        for arg in type_args:
            match = re.search(pattern, arg)
            param = match.group('param')
            raw_value = '"%s"' % match.group('value').strip()
            value = cli.safe_eval(raw_value)
            kwargs[param] = value
        return kwargs

    def run(self, args):

        # Parse type_args or args that are specific to a given Repo type
        repo_kwargs = self.parse_type_args(args.type_args)
        repo_type = repo_kwargs.pop('type', args.type)

        cli.echo()
        if repo_type not in cpenv.repos.registry:
            cli.echo('Error: %s is not a registered repo type.' % args.type)
            cli.echo('Choose from: ' + ', '.join(cpenv.repos.registry.keys()))
            sys.exit(1)

        if cpenv.get_repo(args.name):
            cli.echo('Error: Repo named %s already exists.' % args.name)
            sys.exit(1)

        repo_cls = cpenv.repos.registry[repo_type]
        repo_kwargs['name'] = args.name
        cli.echo('- Checking %s args...' % repo_cls.__name__, end='')
        try:
            repo_cls(**repo_kwargs)
        except Exception as e:
            cli.echo('OOPS!')
            cli.echo()
            cli.echo('Error: Failed to initialize %s' % repo_cls.__name__)
            cli.echo(str(e))
            sys.exit(1)
        cli.echo('OK!')
        cli.echo()

        cli.echo('- Adding repo to config...', end='')
        repo_kwargs['type'] = repo_type
        repo_config = cpenv.read_config('repos', {})
        repo_config[args.name] = repo_kwargs
        cpenv.write_config('repos', repo_config)
        cli.echo('OK!')
        cli.echo()


class RemoveRepo(cli.CLI):
    '''Remove repo by name.'''

    name = 'remove'

    def setup_parser(self, parser):
        parser.add_argument(
            'name',
            help='Name of the repo',
        )

    def run(self, args):
        cli.echo()
        if args.name in ['home', 'user', 'cwd']:
            cli.echo('Error: Can not remove %s repo.' % args.name)

        repo_config = cpenv.read_config('repos', {})
        if args.name not in repo_config:
            cli.echo('Error: Repo named %s not found.' % args.name)
            sys.exit(1)

        cli.echo('- Removing repo from config...', end='')
        repo_config.pop(args.name)
        cpenv.write_config('repos', repo_config)
        cli.echo('OK!')
        cli.echo()


class Version(cli.CLI):
    '''Show version information.'''

    def run(self, args):

        cli.echo()
        cli.echo(cli.format_section(
            'Version Info',
            [
                ('name', cpenv.__name__),
                ('version', cpenv.__version__),
                ('url', cpenv.__url__),
                ('package', utils.normpath(os.path.dirname(cpenv.__file__))),
                ('path', api.get_module_paths()),
            ]
        ), end='\n\n')

        # List package versions
        dependencies = []
        try:
            import Qt
            dependencies.extend([
                ('Qt.py', Qt.__version__),
                ('Qt Binding', Qt.__binding__ + '-' + Qt.__binding_version__),
            ])
        except ImportError:
            pass

        if not dependencies:
            return

        cli.echo(cli.format_section('Dependencies', dependencies), end='\n\n')


def prompt_for_repo(repos, message, default_repo_name='home'):
    '''Prompt a user to select a repository'''

    for i, from_repo in enumerate(repos):
        if from_repo.name == default_repo_name:
            default = i
        if from_repo.name == from_repo.path:
            line = '  [{}] {}'.format(i, from_repo.path)
        else:
            line = '  [{}] {} - {}'.format(
                i,
                from_repo.name,
                from_repo.path,
            )
        cli.echo(line)

    # Prompt user to choose a repo defaults to home
    cli.echo()
    choice = cli.prompt('{}: [{}]'.format(message, default))

    if not choice:
        choice = default
    else:
        choice = int(choice)
        if choice > len(repos) - 1:
            cli.echo()
            cli.echo('Error: {} is not a valid choice'.format(choice))
            sys.exit(1)

    # Get the repo the user chose
    return repos[choice]


def main():
    cli.run(CpenvCLI, sys.argv[1:])


if __name__ == '__main__':
    main()
