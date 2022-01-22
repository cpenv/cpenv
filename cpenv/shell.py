# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import fnmatch
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


def get_shell():
    '''Get an approriate shell to use for a subshell.

    1. Use value of CPENV_SUBSHELL env var
    2. Attempt to walk up process tree using psutil
    3. Use a default shell (May not match with parent shell)

    Default Shells:
        win: powershell.exe
        mac: bash
        linux: bash
    '''

    # Get preferred shell from
    preferred_shell = os.getenv('CPENV_SUBSHELL')
    if preferred_shell:
        return preferred_shell

    # Attempt to find parent shell using psutil
    try:
        import psutil
        supported_shells = [
            'powershell.exe',
            'cmd.exe',
            'powershell',
            'cmd',
            'bash',
            'sh',
            'fish',
            'xonsh',
            'zsh',
            'csh',
        ]

        process_parents = psutil.Process().parents()
        for proc in process_parents[::-1]:
            exe = proc.exe()
            exe_name = os.path.basename(exe)
            if exe_name in supported_shells:
                return exe
    except ImportError:
        pass

    # Fallback to a default shell
    return {
        'win': 'powershell.exe',
        'linux': 'bash',
        'mac': 'bash',
    }[compat.platform]


def get_prompt(shell, prefix, colored=True):
    '''Generate a prompt with a given prefix

    linux/osx: [prefix] user@host cwd $
          win: [prefix] cwd:
    '''

    if shell.endswith('cmd.exe'):
        return '{} $P$G'.format(prefix)

    if shell.endswith('powershell.exe'):
        return "'{} PS ' + $(get-location) + '> '".format(prefix)

    if shell.endswith('bash'):
        if colored:
            return (
                '{} '  # White prefix
                '\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\] '  # Green user@host
                '\\[\\033[01;34m\\]\\w $ \\[\\033[00m\\]'  # Blue cwd $
            ).format(prefix)
        return '{} \\u@\\h \\w $ '.format(prefix)


def get_subshell_command(prefix):
    '''Return a command to launch a subshell'''

    shell = get_shell()
    try:
        disable_prompt = int(os.getenv('CPENV_DISABLE_PROMPT', 0))
    except:
        disable_prompt = 0

    prompt = get_prompt(shell, prefix)

    if shell.endswith('cmd.exe'):
        if not disable_prompt:
            os.environ['PROMPT'] = prompt
        return [shell, '/K']

    if shell.endswith('powershell.exe'):
        args = [shell, '-NoExit', '-NoLogo']
        if not disable_prompt:
            args += ['-Command', "function Prompt {%s}" % prompt]
        return args

    if shell.endswith('bash'):
        if not disable_prompt:
            os.environ['PROMPT'] = prompt
        return [shell, binpath('subshell.sh')]

    return [shell]


def launch(prefix='[*]'):
    '''Launch a subshell'''

    shell_cmd = get_subshell_command(prefix)
    subprocess.call(shell_cmd, env=dict(os.environ))
