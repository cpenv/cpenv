# -*- coding: utf-8 -*-


class Repo(object):
    '''A source of modules.

    Provides methods for listing, finding, uploading, and downloading modules.
    '''

    type_name = 'repo'

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        args = []
        for attr in ['name', 'path']:
            if hasattr(self, attr):
                args.append('{}={!r}'.format(attr, getattr(self, attr)))
        return '<{}>({})'.format(type(self).__name__, ', '.join(args))

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

    def get_data(self, module_spec):
        '''Given a module_spec, return a Module's config(module.yml) dict.

        If possible this should be implemented for all Repos, however, it
        is not used during module resolution. It is only used to provide
        a richer view of Modules in Repos by UI implementations.
        '''

        return {}
