# -*- coding: utf-8 -*-


class Repo(object):
    '''A source of modules.

    Provides methods for listing, finding, uploading, and downloading modules.
    '''

    type_name = 'repo'

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        name = self.name
        path = getattr(self, 'path', '')
        if name == path:
            return '<{}>(name="{}")'.format(
                    self.__class__.__name__,
                    name,
                )
        else:
            return '<{}>(name="{}", path="{}")'.format(
                self.__class__.__name__,
                name,
                path,
            )

    def find(self, requirement):
        '''Given a requirement, return a list of ModuleSpecs that match.

        Should be ordered from best to worst match.
        '''

        return NotImplemented

    def list(self):
        '''Return a list of ModuleSpecs in this Repo.'''

        return NotImplemented

    def download(self, module_spec, where, overwrite=False):
        '''Given a module_spec and output path, download it from this Repo.

        Return a newly downloaded Module.
        '''

        return NotImplemented

    def upload(self, module, overwrite=False):
        '''Given a module, upload it to this Repo.

        Return a ModuleSpec.
        '''

        return NotImplemented

    def remove(self, module_spec):
        '''Given a module_spec, remove it from this repo.'''

        return NotImplemented
