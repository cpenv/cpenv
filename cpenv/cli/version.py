import cpenv
from cpenv import api, paths
from cpenv.cli import core


class Version(core.CLI):
    '''Show version information.'''

    def run(self, args):

        core.echo()
        core.echo(core.format_section(
            'Version Info',
            [
                ('name', cpenv.__name__),
                ('version', cpenv.__version__),
                ('url', cpenv.__url__),
                ('package', paths.parent(cpenv.__file__)),
                ('path', api.get_module_paths()),
            ]
        ))
        core.echo()

        # List package versions
        dependencies = []
        try:
            import Qt
            dependencies.extend([
                ('Qt.py', Qt.__version__),
                ('Qt Binding', Qt.__binding__ + '-' + Qt.__binding_version__),
            ])
        except ImportError:
            pass

        if not dependencies:
            return

        core.echo(core.format_section('Dependencies', dependencies), end='\n\n')
