

class Repo(object):
    '''Base class for all repos.'''

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        '''Subclasses should implement this method to ensure'''

        return NotImplemented

    def __hash__(self, other):
        '''Subclasses should provide a viable hash for their Repo.'''

        return NotImplemented

    def __repr__(self):
        '''Subclasses should implement this method to provide a nicely
        formatted str representation.'''

        return super(Repo, self).__str__()

    def find_module(self, requirement):
        '''Subclasses must return a ModuleSpec object matching requirement.'''

        return NotImplemented

    def list_modules(self, requirement=None):
        '''Return a list of ModuleSpec objects matching requirement.

        If requirement is None, list all ModuleSpecs available in the repo.
        '''

        return NotImplemented

    def clone_module(self, requirement, where):
        '''Download a module using a ModuleSpec to the specified directory.'''

        return NotImplemented

    def publish_module(self, module):
        '''Upload a module'''

        return NotImplemented
