# -*- coding: utf-8 -*-

import os
from .packages import yaml
from .utils import unipath
from .models import VirtualEnvironment


class EnvironmentCache(set):
    '''Cache VirtualEnvironment objects to disk.'''

    def __init__(self, path):
        super(EnvironmentCache, self).__init__()
        self.path = path

        if not os.path.exists(self.path):
            root = os.path.dirname(self.path)
            if not os.path.exists(root):
                os.makedirs(root)
            with open(self.path, 'a'):
                os.utime(self.path, None)
        else:
            self.load()
            self.validate()

    def find(self, path):

        for env in self:
            if env.name == path:
                return env
            if os.path.abspath(env.root) == os.path.abspath(path):
                return env

        return None

    def validate(self):
        '''Validate all the entries in the environment cache.'''

        for env in list(self):
            if not env.exists or not env.is_valid:
                self.remove(env)

    def load(self):
        '''Load the environment cache from disk.'''

        if not os.path.exists(self.path):
            return

        with open(self.path, 'r') as f:
            env_data = yaml.load(f.read())

        if env_data:
            for env in env_data:
                self.add(VirtualEnvironment(env['root']))

    def clear(self):
        '''Clear the environment cache'''
        for env in list(self):
            self.remove(env)

    def save(self):
        '''Save the environment cache to disk.'''

        env_data = [dict(name=env.name, root=env.root) for env in self]
        encode = yaml.safe_dump(env_data, default_flow_style=False)

        with open(self.path, 'w') as f:
            f.write(encode)


EnvironmentCache = EnvironmentCache(unipath('~/.cpenv', 'envcache.yml'))
