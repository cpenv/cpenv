# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
import subprocess

# Local imports
from . import compat


def binpath(*paths):
    '''Like os.path.join but acts relative to this packages bin path.'''

    package_root = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(package_root, 'bin', *paths))


def run(*args, **kwargs):
    '''Returns True if successful, False if failure'''

    kwargs.setdefault('env', os.environ)
    kwargs.setdefault('shell', True)

    try:
        subprocess.check_call(' '.join(args), **kwargs)
        return True
    except subprocess.CalledProcessError:
        print('Error running: {}'.format(args))
        return False


def get_subshell_command():
    '''Return a command to launch a subshell'''

    if compat.platform == 'win':
        return ['cmd.exe', '/K']

    elif compat.platform == 'linux':
        ppid = os.getppid()
        ppid_cmdline_file = '/proc/{0}/cmdline'.format(ppid)
        try:
            with open(ppid_cmdline_file) as f:
                command = f.read()
            if command.endswith('\x00'):
                command = command[:-1]
            command = command.split('\x00')
            return command + [binpath('subshell.sh')]
        except Exception:
            command = 'bash'

    else:
        command = 'bash'

    return [command, binpath('subshell.sh')]


def prompt(prefix='', colored=True):
    '''Generate a prompt with a given prefix

    linux/osx: [prefix] user@host cwd $
          win: [prefix] cwd:
    '''

    if compat.platform == 'win':
        return '{0} $P$G'.format(prefix)
    else:
        if colored:
            return (
                '{0} '  # White prefix
                '\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\] '  # Green user@host
                '\\[\\033[01;34m\\]\\w $ \\[\\033[00m\\]'  # Blue cwd $
            ).format(prefix)
        return '{0} \\u@\\h \\w $ '.format(prefix)


def launch(prompt_prefix=None):
    '''Launch a subshell'''

    if prompt_prefix is not None:
        os.environ['PROMPT'] = prompt(prompt_prefix)

    subprocess.call(get_subshell_command(), env=dict(os.environ))
