

class Repo(object):
    '''Base class for all repos.'''

    def __init__(self, name):
        self.name = name

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

    def localize_module(self, spec):
        '''If you are writing a remote Repo, like a GitRepo for example...

        This method should download the module from the remote location and
        place it into the home modules path (get_home_modules_path()).

        You must return the localized Module object.
        '''

    def find_module(self, matching):
        '''Subclasses can return either Module objects for a local Repo or
        ModuleSpec objects for a remote Repo.'''

        return NotImplemented

    def list_modules(self, matching=None):
        '''Return a list of ModuleSpec objects.

        Arguments:
            matching (str) - string used to filter modules
        '''

        return NotImplemented

    def clone_module(self, module, where):
        '''Clone a Module to the specified directory.

        If you're writing a remote Repo, this should accept a ModuleSpec and
        download the module.
        '''

        return NotImplemented

    def publish_module(self, module):
        '''Publish a module to this repo.

        Return a new Module or ModuleSpec object.'''

        return NotImplemented
