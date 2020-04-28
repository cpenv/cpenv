# -*- coding: utf-8 -*-
'''Minimal and standalone CLI framework.'''
from __future__ import absolute_import, print_function

# Standard library imports
import argparse
import os
import sys
from itertools import zip_longest
from textwrap import wrap


version = sys.version_info[0]
is_py2 = version == 2
is_py3 = version == 3
missing = object()


class CLI(object):

    name = None
    usage = None
    description = None

    def __init__(self, parent=None):
        self.parent = parent
        self._commands = {c.name: c for c in self.commands()}

    @property
    def name(self):
        return self.__class__.__name__.lower()

    @property
    def description(self):
        return self.__doc__.split('\n')[0].rsplit('.', 1)[0]

    @property
    def fullname(self):
        name = [self.name]
        if self.parent:
            name.insert(0, self.parent.fullname)
        return ' '.join(name)

    def commands(self):
        return []

    def get_command(self, name):
        return self._commands.get(name, None)

    def format_commands(self):
        if not self._commands:
            return ''

        return format_section(
            'COMMAND',
            [
                (k, v.description)
                for k, v in self._commands.items()
            ],
        )

    @property
    def parser(self):
        if hasattr(self, '_parser'):
            return self._parser

        self._parser = argparse.ArgumentParser(
            prog=self.fullname,
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage=self.usage,
            add_help=False,
        )
        self._parser.add_argument(
            '-h',
            '--help',
            help='show this help message and exit',
            action='store_true',
            dest='help'
        )
        self.setup_parser(self._parser)

        argument_names = [a.dest for a in self._parser._actions]
        if self._commands and 'command' not in argument_names:
            self._parser.add_argument(
                'command',
                help='subcommand to run.',
                action='store',
                nargs='?',
            )
            self._parser.epilog = self.format_commands()

        return self._parser

    def setup_parser(self, parser):
        '''Subclasses implement this method to parse arguments.'''

    def run(self, args):
        '''Subclasses implement this method.'''
        self.parser.print_help()


def prompt(message):
    '''Prompt a user for input'''
    if is_py2:
        return raw_input(message)

    return input(message)


def format_section(header, rows):

    width = max(len(max(rows, key=lambda x: len(x[0]))), 8) + 2

    lines = [header]
    for key, value in sorted(rows):

        # Handle lists - one value per line
        additional_lines = []
        if isinstance(value, (list, tuple)):
            if len(value) == 1:
                value = value[0]
            elif len(value) > 1:
                additional_lines = value[1:]
                value = value[0]

        line = wrap(
            '{1:<{0}}  {2}'.format(width, key, value),
            initial_indent='  ',
            subsequent_indent=' ' * (width + 4),
        )
        lines.append('\n'.join(line))

        for value in additional_lines:
            line = wrap(
                '{1:<{0}}  {2}'.format(width, '', value),
                initial_indent='  ',
                subsequent_indent=' ' * (width + 4),
            )
            lines.append('\n'.join(line))

    return '\n'.join(lines)


def columns_to_rows(items, columns, width):

    row_count = int(len(items) / columns + 1)

    # Build columns
    columns = []
    for i in range(0, len(items), row_count):
        column = [elide(item, width) for item in items[i:i + row_count]]
        if len(column) < row_count:
            column += [''] * (row_count - len(column))
        columns.append(column)

    # Transpose for rows
    rows = [list(row) for row in zip_longest(*columns)]
    return rows


def format_columns(header, items, indent='    '):

    size = os.get_terminal_size()
    width = max(len(max(items, key=len)), 18) + 4
    columns = int((size.columns) / (width + 4))

    lines = [header]
    for row in columns_to_rows(items, columns, width):
        lines.append((
            indent +
            '{:<{width}} ' * columns
        ).format(*row, width=width))

    return '\n'.join(lines)


def elide(text, width):
    if len(text) > width:
        return text[:width - 3] + '...'
    return text


def run(cli, unparsed_args=missing):
    '''Execute a CLI command.'''

    if unparsed_args is missing:
        unparsed_args = sys.argv[1:]

    try:
        cli = cli()
    except TypeError as e:
        if 'object is not callable' not in str(e):
            raise

    # First parse used to pass arguments along to subcommands
    try:
        args, more_args = cli.parser.parse_known_args(unparsed_args)
    except SystemExit:
        if '-h' in unparsed_args or '--help' in unparsed_args:
            cli.parser.print_help()
            sys.exit()
        raise

    global_options = [('help', '-h'), ('verbose', '-v')]
    options = [f for n, f in global_options if args.__dict__.get(n, False)]

    if 'command' in args:
        cli_command = cli.get_command(args.command)
        if cli_command:
            # Recursively execute subcommand
            args = options + more_args
            return run(cli_command, args)

        if cli_command is not None:
            cli.parser.print_usage()
            print('error: unrecognized command "%s"' % args.command)
            print('       expected one of %s' % list(cli._commands.keys()))
            sys.exit(2)

    # Final parse for validation before run
    args = cli.parser.parse_args(unparsed_args)
    if args.help:
        cli.parser.print_help()
        sys.exit()

    return cli.run(args)
