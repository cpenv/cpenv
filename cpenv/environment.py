# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

missing = object()


class Environment(object):
    '''An object that represents a list of requirements.

    Once you have activated some modules, you can save them as an Environment
    to be activated later. Think of them as an alias for activating a list
    of module requirements.

    # TODO: Add the ability to save and activate Environments directly from
    all Repos. The Shotgun app tk-cpenv implements this functionality
    internally, it should be moved to cpenv at some point and the code related
    to Environments in tk-cpenv can be removed.
    '''

    def __init__(self, name, data=None, path=None):
        self.name = name
        self.data = data or {'name': name, 'requires': []}
        self.path = path

    def get(self, key, default=missing):
        if key not in self.data and default is not missing:
            return default

        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

    @property
    def requires(self):
        return self.data['requires']
