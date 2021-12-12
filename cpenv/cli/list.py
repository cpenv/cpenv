from cpenv import api
from cpenv.cli import core
from cpenv.module import (
    is_partial_match,
    sort_modules,
)


class List(core.CLI):
    '''List active and available Modules.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'requirement',
            help='Space separated list of modules.',
            nargs='?',
            default=None,
        )
        parser.add_argument(
            '--repo',
            help='List modules only in this repo.',
            default=None,
        )
        parser.add_argument(
            '--verbose', '-v',
            help='Print more module info.',
            action='store_true',
        )

    def run(self, args):

        found_modules = False

        core.echo()
        active_modules = api.get_active_modules()
        if args.requirement:
            active_modules = [
                m for m in active_modules
                if is_partial_match(args.requirement, m)
            ]

        if active_modules:
            found_modules = True
            core.echo(core.format_columns(
                '[*] Active',
                [m.real_name for m in sort_modules(active_modules)],
            ))
            core.echo()

        repos = api.get_repos()
        if args.repo:
            repos = [api.get_repo(args.repo)]

        for repo in repos:
            if args.requirement:
                repo_modules = repo.find(args.requirement)
            else:
                repo_modules = repo.list()

            module_names = []
            for module in sort_modules(repo_modules):
                if module in active_modules:
                    module_names.append('* ' + module.real_name)
                else:
                    module_names.append('  ' + module.real_name)

            if module_names:
                found_modules = True
                if repo.name != repo.path:
                    header = repo.name + ' - ' + repo.path
                else:
                    header = repo.name
                core.echo(core.format_columns(
                    '[ ] ' + header,
                    module_names,
                    indent='  ',
                ))
                core.echo()

        if not found_modules:
            core.echo('No modules are available.')
