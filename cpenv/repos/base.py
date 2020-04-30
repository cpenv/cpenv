

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

    def localize_module(self, spec):
        '''If you are writing a remote Repo, like a GitRepo for example...

        This method should download the module from the remote location and
        place it into the home modules path (get_home_modules_path()).

        You must return the localized Module object.
        '''

    def find_module(self, requirement):
        '''Subclasses can return either Module objects for a local Repo or
        ModuleSpec objects for a remote Repo.'''

        return NotImplemented

    def list_modules(self, requirement=None):
        '''Return a list of Module or ModuleSpec objects matching requirement.

        If no requirement is provided return all items in the Repo.
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
