# -*- coding: utf-8 -*-


class Repo(object):
    '''Base class for all Repos.

    A Repo is a source of modules. They can be local or remote so long as they
    provide this interface.
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

    def clear_cache(self):
        '''Subclasses that implement caching should implement this method
        so that cpenv can clear the cache when necessary. Like after copying
        or localizing modules.
        '''
        return NotImplemented

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

    def get_size(self, module_spec):
        '''Given a module_spec, return the size of a module in the repo.

        For remote repositories this may mean reading a field in a databse.
        For the LocalRepo it means getting the combined size of the module
        folder's contents.

        Repos should implement this method to full support progress bars
        while publishing and localizing modules.

        Return -1 when size if the size is unavailable.
        '''
        return -1

    def get_thumbnail(self, module_spec):
        '''Given a module_spec, return the path to a thumbnail.

        Remote repos should download a thumbnail to the cache/icons:
            cache_path = cpenv.get_cache_path('icons', 'cached-0.1.0.png')

        Return None when no thumbnail is available.
        '''
        return

    def list_environments(self, filters=None):
        '''Return a list of Environments in this repo.

        Filters should be a dict containing fields to match in the list of
        results for example:
            {
                'name': 'My*',
                'requires': ['my_module'],
            }

        The above filters should return a list of Environments with names
        beginning with My and requires containing my_module.
        '''

        return []

    def save_environment(self, name, data, force=False):
        '''Save an environment to this repo.

        This method needs to store an Environment within the Repo. This could
        mean saving to a database or to a file on disk in the case of
        local repositories.
        '''

        return NotImplemented

    def remove_environment(self, name):
        '''Removes an Environment from this repo.'''

        return NotImplemented
