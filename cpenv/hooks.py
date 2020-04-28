# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import os
from types import ModuleType

# Local imports
from .utils import normpath

'''
cpenv.hooks
===========
Defines the :class:`HookFinder` object used to find and execute hooks.
'''
import os
from types import ModuleType
from .utils import unipath
from .log import logger


class HookFinder(object):
    '''Find python hooks by name in the provided path.

    usage::

        >>> hook_finder = HookFinder('~/.cpenv/hooks')
        >>> hook = hook_finder('precreate')
        >>> hook.run(env=VirtualEnvironment('path/to/env'))
    '''

    def __init__(self, *hook_paths):
        self.hook_paths = hook_paths

    def _find_pyfile(self, hook_name):
        for path in self.hook_paths:
            hook_path = unipath(path, hook_name + '.py')
            if os.path.exists(hook_path):
                return hook_path

    def find(self, hook_name):

        hook_path = self._find_pyfile(hook_name)

        if not hook_path:
            return

        try:
            with open(hook_path, 'r') as f:
                code = compile(f.read(), '', 'exec')
        except SyntaxError as e:
            logger.error('SyntaxError compiling hook: {}'.format(e))
            raise

        hook = ModuleType(hook_name)
        hook.__file__ = hook_path

        try:
            exec(code, hook.__dict__)
            return hook
        except Exception:
            logger.error('Error executing hook: {}'.format(hook_path))
            raise

    __call__ = find


def get_global_hook_path():
    '''Returns the global hook path'''

    return unipath(os.environ.get('CPENV_HOME', '~/.cpenv'), 'hooks')


def run_global_hook(hook_name, *args):
    '''Attempt to run a global hook by name with args'''

    hook_finder = HookFinder(get_global_hook_path())
    hook = hook_finder(hook_name)
    if hook:
        hook.run(*args)
