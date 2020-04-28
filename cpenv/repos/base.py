

class Repo(object):
    '''Base class for all repos'''

    def find_module(self, requirement):
        '''Return a single ModuleSpec object matching the requirement.'''

    def list_modules(self, requirement=None):
        '''Return a list of ModuleSpec objects matching the requirement.

        If no requirement is provided, list all ModuleSpecs available in the
        repo.
        '''

    def download_module(self, module_spec, where):
        '''Download a module using a ModuleSpec to the specified directory.'''

    def upload_module(self, module):
        '''Upload a module'''
