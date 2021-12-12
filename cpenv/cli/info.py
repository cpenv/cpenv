import sys

from cpenv import api, reporter
from cpenv.resolver import ResolveError
from cpenv.cli import core


class Info(core.CLI):
    '''Show Module info'''

    usage = 'cpenv info [-h] [<modules>...]'

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='*',
        )
        parser.add_argument(
            '--key',
            help=(
                'Specify the name of a key like "path" or "version". '
                'When provided this command will print the value of the key.'
            ),
            default=None,
        )
        parser.add_argument(
            '--repo',
            help='Get repo info instead of module info.',
            action='store_true',
        )
        parser.add_argument(
            '--home',
            help='Get the path to the cpenv home directory.',
            action='store_true',
        )
        parser.add_argument(
            '--cache',
            help='Get the path to the cpenv cache directory.',
            action='store_true',
        )

    def _get_key(self, obj, key):
        try:
            return eval('obj.' + key)
        except Exception as e:
            core.echo('Error: %s' % e)
            sys.exit(1)

    def run(self, args):
        if args.home:
            core.echo(api.get_home_path())
            return

        if args.cache:
            core.echo(api.get_cache_path())
            return

        # Key mode - print a key's value of a module or repo.
        if args.key:
            reporter.set_reporter(reporter.Reporter())
            if args.repo:
                objects = []
                for repo_name in args.modules:
                    repo = api.get_repo(repo_name)
                    if repo is None:
                        core.echo('Could not find repo %s' % repo_name)
                        sys.exit(1)
                    objects.append(repo)
            else:
                try:
                    objects = api.resolve(args.modules)
                except ResolveError:
                    sys.exit(1)

            value = self._get_key(objects[0], args.key)
            core.echo(value)
            return

        # Normal mode - resolve repos or modules and show info.
        core.echo()
        if args.repo:
            repos = []
            for repo_name in args.modules:
                repo = api.get_repo(repo_name)
                if repo is None:
                    core.echo('Could not find repo %s' % repo_name)
                    sys.exit(1)
                repos.append(repo)

            for repo in repos:
                core.echo(core.format_section(
                    repo.name,
                    [
                        ('name', repo.name),
                        ('path', repo.path),
                        ('type', str(type(repo))),
                        ('type_name', repo.type_name),
                    ]
                ))
                core.echo()
            return
        else:
            try:
                module_specs = api.resolve(args.modules)
            except ResolveError:
                sys.exit(1)

            core.echo()
            for spec in module_specs:
                core.echo(core.format_section(
                    spec.qual_name,
                    [
                        (k, str(v))
                        for k, v in sorted(spec._asdict().items())
                    ],
                ))
                core.echo()
            return
