# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import sys

# Local imports
import cpenv
from cpenv import (
    ResolveError,
    api,
    cli,
    shell,
    utils,
    versions,
)
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
        print('  - Resolving modules')
        try:
            modules = api.activate(*args.modules)
        except ResolveError:
            print()
            print('Error: failed to resolve %s' % args.modules)
            sys.exit(1)

        print()
        for module in modules:
            print('%s' % module.name)
        print()

        print('  - Launching subshell')
        shell.launch('[*]')


class List(cli.CLI):
    '''List active and available modules.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='*',
        )

    def run(self, args):
        print()
        active_modules = api.get_active_modules()
        if active_modules:
            print(cli.format_columns(
                '[*] Active',
                [m.name for m in active_modules],
            ))

        print()
        available_modules = api.get_modules()
        if available_modules:
            print(cli.format_columns(
                '[ ] Available Modules',
                [m.name for m in available_modules],
            ))
        else:
            print('No modules available.')


def main():
    cli.run(CpenvCLI, sys.argv[1:])


if __name__ == '__main__':
    main()
