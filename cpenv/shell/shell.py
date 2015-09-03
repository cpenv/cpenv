# -*- coding: utf-8 -*-
'''
shell
=====
Cross-platform ShellScript Generation.

::

    script = ShellScript()
    script.set_env('PATH', ['a/great/path'])
    script.set_env('INTVAR', 1)
    script.set_env('STRVAR', 'myGreatString')
    script.set_platform('win')
    with open('add_to_path.bat', 'w') as f:
        f.write(script.as_string())

'''

import collections
import os
from .. import platform
from ..utils import unipath
from abc import ABCMeta, abstractmethod
ABC = ABCMeta(str("ABC"), (), {}) # 2n3 compatible metaclassing


class BaseCommands(ABC):
    '''Abstract set of shell commands'''

    def echo(self, value):
        return 'echo {}'.format(value)

    def run_cmd(self, *args):
        return ' '.join(args)

    def run_py(self, *args):
        return 'run_py ' + ' '.join(args)

    @abstractmethod
    def rmtree(self, path):
        '''Remove a directory tree'''

    @abstractmethod
    def set(self, var, value):
        '''Set a variable'''

    @abstractmethod
    def set_env(self, var, value):
        '''Set an environment variable'''

    @abstractmethod
    def unset(self, var):
        '''Unset a variable'''

    @abstractmethod
    def unset_env(self, var):
        '''Unset an environment variable'''

    @abstractmethod
    def run_script(self, script_path):
        '''Run a script'''

    @abstractmethod
    def source(self, script_path):
        '''Alias for run_script'''

    @abstractmethod
    def call(self, script_path):
        '''Alias for run_script'''


class BatchCommands(BaseCommands):
    '''Implements all BaseCommands in batch.'''

    def rmtree(self, path):
        return 'rmdir /s/q {}'.format(path)

    def set_env(self, var, value):
        return 'set "{}={}"'.format(var, value)

    set = set_env

    def unset_env(self, var):
        return 'set {}='.format(var)

    unset=unset_env

    def run_script(self, script_path):
        return 'call {}'.format(script_path)

    source = run_script
    call = run_script


class BashCommands(BaseCommands):
    '''Implements all BaseCommands in bash.'''

    def rmtree(self, path):
        return 'rm -rf {}'.format(path)

    def set_env(self, var, value):
        return 'export {}="{}"'.format(var, value)

    def set(self, var, value):
        return '{}="{}"'.format(var, value)

    def unset_env(self, var):
        return 'unset {}'.format(var)

    unset=unset_env

    def run_script(self, script_path):
        return 'source {}'.format(script_path)

    source = run_script
    call = run_script


class ShellScript(list):
    '''Class providing cross-platform commands for bash and batch.

    :param platform: "win", "osx", or "linux" (default=current platform)'''

    def __init__(self, *args):
        super(ShellScript, self).__init__(*args)
        self._env = os.environ.data.copy()
        self.bashcommands = BashCommands()
        self.batchcommands = BatchCommands()
        self._platform = platform

        def command(name):
            '''Returns a partial for a command name based on platform.
            Seems a bit magical...'''
            script = self
            def command_partial(*args, **kwargs):
                def command_caller():
                    if script.get_platform() == 'win':
                        fn = getattr(script.batchcommands, name)
                    else:
                        fn = getattr(script.bashcommands, name)
                    return fn(*args, **kwargs)
                script.append(command_caller)
            return command_partial

        for k in dir(BaseCommands):
            if not k.startswith('__'):
                setattr(self, k, command(k))

    def __repr__(self):
        return '<ShellScript>(platform={})'.format(platform)

    def get_platform(self):
        return platform

    def set_platform(self, platform):
        self._platform = platform

    def as_string(self):
        if self._platform == 'win':
            lines = ['@echo off']
        else:
            lines = ['#!/bin/bash']

        for cmd in self:
            lines.append(cmd())

        return '\n'.join(lines)


class BashScript(ShellScript):
    '''BashScript == ShellScript().set_platform('linux')'''

    def __init__(*args):
        super(BashScript, self).__init__(*args)
        self.set_platform('linux')


class BatchScript(ShellScript):
    '''BatchScript() == ShellScript().set_platform('win')'''

    def __init__(*args):
        super(BashScript, self).__init__(*args)
        self.set_platform('win')
