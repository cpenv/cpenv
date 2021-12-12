from cpenv import api, shell
from cpenv.resolver import ResolveError
from cpenv.cli import core


class Activate(core.CLI):
    '''Activate a list of Modules or an Environment.

    Examples:
      cpenv activate module_a module_b
      cpenv activate module_a-1.0 module_b 0.2.0
      cpenv activate my_environment
      cpenv activate --env my_environment

    Note:
      Use the --env flag to specifically activate an Environment by name
      rather than checking for modules first. Use the "cpenv env" command to
      manage Environments.
    '''

    usage = 'cpenv activate [-h] [<modules> or <environment>...]'

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='+',
        )
        parser.add_argument(
            '--env',
            help='Activate an Environment. (False)',
            action='store_true',
        )

    def run(self, args):

        core.echo()

        if args.env:
            try:
                api.activate_environment(args.modules[0])
            except ResolveError as e:
                core.echo(str(e))
                core.exit(1)
        else:
            try:
                api.activate(args.modules)
            except ResolveError:
                api.activate_environment(args.modules[0])
            except ResolveError:
                core.exit(1)

        core.echo('- Launching subshell...')
        core.echo()
        core.echo('  Type "exit" to deactivate.')
        core.echo()
        shell.launch('[*]')
