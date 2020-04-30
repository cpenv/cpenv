# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import sys

# Local imports
import cpenv
from cpenv import ResolveError, api, cli, shell, utils
from cpenv.module import parse_module_path


class CpenvCLI(cli.CLI):
    '''Cpenv Command Line Interface.'''

    name = 'cpenv'
    usage = 'cpenv [-h] <command> [<args>...]'

    def commands(self):
        return [
            Version(self),
            Create(self),
            Activate(self),
            List(self),
        ]


class Version(cli.CLI):
    '''Show version information.'''

    def run(self, args):

        print()
        print(cli.format_section(
            'Version Info',
            [
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

        print(cli.format_section('Dependencies', dependencies), end='\n\n')


class Create(cli.CLI):
    '''Create a new module.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'where',
            help='Path to new module',
        )
        parser.add_argument(
            '--name', '-n',
            help='Name of new module',
            default='',
        )
        parser.add_argument(
            '--version', '-v',
            help='Version of the new module',
            default='',
        )
        parser.add_argument(
            '--description', '-d',
            help='Details about the module',
            default='',
        )
        parser.add_argument(
            '--author', '-a',
            help='Author of the module',
            default='',
        )
        parser.add_argument(
            '--email', '-e',
            help="Author's email address",
            default='',
        )

    def run(self, args):
        print()
        where = utils.normpath(args.where)
        name, version = parse_module_path(where)

        api.create(
            where=where,
            name=args.name or name,
            version=args.version or version.string,
            description=args.description,
            author=args.author,
            email=args.email,
        )


class Activate(cli.CLI):
    '''Activate a list of modules.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='*',
        )

    def run(self, args):
        print()
        print('- Resolving modules')
        try:
            activated_modules = api.activate(*args.modules)
        except ResolveError:
            print()
            print('Error: failed to resolve %s' % args.modules)
            sys.exit(1)

        print()
        for module in activated_modules:
            print('  ' + module.real_name)
        print()

        print('- Launching subshell')
        shell.launch('[*]')


class Localize(cli.CLI):
    '''Localize a list of modules.

    Downloads modules from a remote Repo and places them in the home LocalRepo
    by default. Use the --to_repo option to specify a LocalRepo.
    '''

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='*',
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
            repos = [r for r in repos if isinstance(repo, LocalRepo)]
            to_repo = prompt_for_repo(
                [r for r in api.get_repos() if isinstance(repo, LocalRepo)],
                'Choose a repo to localize to',
                default_repo_name='home',
            )

        cli.echo()
        cli.echo(
            '- Localizing %s to %s...' % (args.modules, to_repo.name),
            end='',
        )
        modules = api.localize(*args.modules, to_repo, args.overwrite)
        cli.echo('OK!')
        cli.echo()

        cli.echo()
        cli.echo('Localized the following modules:')
        for module in modules:
            click.echo('  %s - %s' % (module.real_name, module.path))


class Remove(cli.CLI):
    '''Permanently remove a module from a repo.'''

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

        cli.echo()
        cli.echo(
            '- Finding module %s to %s...' % (args.module, from_repo.name),
            end='',
        )
        module = from_repo.find_module(args.module)
        if not module:
            click.echo('ER!', end='\n\n')
            click.echo(
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

        cli.echo('- Removing module...', end='')
        api.remove(module, from_repo)
        cli.echo('OK!', end='\n\n')

        cli.echo('Successfully removed module.')

        else:
            print('No modules available.')


def main():
    cli.run(CpenvCLI, sys.argv[1:])


if __name__ == '__main__':
    main()
