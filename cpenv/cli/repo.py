import argparse
import re

from cpenv import api, repos
from cpenv.cli import core


class Repo(core.CLI):
    '''
    Manage, Configure and list Repos.

    Repos are sources of Modules. A Repo can be local or remote. Modules
    stored in remote Repos will be localized to a local repo prior to
    activation or explicitly by using "cpenv localize".
    '''

    def commands(self):
        return [
            ListRepo(self),
            AddRepo(self),
            RemoveRepo(self),
        ]


class ListRepo(core.CLI):
    '''List configured repos'''

    name = 'list'

    def run(self, args):

        core.echo()
        core.echo('Repos in order of resolution:')
        for i, repo in enumerate(api.get_repos()):
            if repo.path == repo.name:
                core.echo('  [{}] {}  {}'.format(
                    i,
                    type(repo).__name__,
                    repo.path,
                ))
            else:
                core.echo('  [{}] {}  {}  {}'.format(
                    i,
                    type(repo).__name__,
                    repo.name,
                    repo.path,
                ))


class AddRepo(core.CLI):
    '''Add a new repo.

    LocalRepo:
        cpenv repo add custom --path=~/custom_repo

    ShotgunRepo:
        cpenv repo add my_shotgun --type=shotgun --base_url=https://my.shotgunstudio.com --script_name=cpenv --api_key=secret
    '''

    name = 'add'

    def setup_parser(self, parser):
        parser.add_argument(
            '--type',
            help='Type of repo',
            choices=['local', 'shotgun'],
            default='local',
        )
        parser.add_argument(
            'name',
            help='Name of the repo',
        )
        parser.add_argument(
            'type_args',
            help='Type specific arguments.',
            nargs=argparse.REMAINDER,
        )

    def parse_type_args(self, type_args):
        pattern = (
            r'-{1,2}(?P<param>[a-zA-Z0-9_]+)=*\s*'
            r'"?(?P<value>.+)"?'
        )
        kwargs = {}
        for arg in type_args:
            match = re.search(pattern, arg)
            param = match.group('param')
            raw_value = '"%s"' % match.group('value').strip()
            value = core.safe_eval(raw_value)
            kwargs[param] = value
        return kwargs

    def run(self, args):

        # Parse type_args or args that are specific to a given Repo type
        repo_kwargs = self.parse_type_args(args.type_args)
        repo_type = repo_kwargs.pop('type', args.type)

        core.echo()
        if repo_type not in repos.registry:
            core.echo('Error: %s is not a registered repo type.' % args.type)
            core.echo('Choose from: ' + ', '.join(repos.registry.keys()))
            core.exit(1)

        if api.get_repo(args.name):
            core.echo('Error: Repo named %s already exists.' % args.name)
            core.exit(1)

        repo_cls = repos.registry[repo_type]
        repo_kwargs['name'] = args.name
        core.echo('- Checking %s args...' % repo_cls.__name__, end='')
        try:
            repo_cls(**repo_kwargs)
        except Exception as e:
            core.echo('OOPS!')
            core.echo()
            core.echo('Error: Failed to initialize %s' % repo_cls.__name__)
            core.echo(str(e))
            core.exit(1)
        core.echo('OK!')
        core.echo()

        core.echo('- Adding repo to config...', end='')
        repo_kwargs['type'] = repo_type
        repo_config = api.read_config('repos', {})
        repo_config[args.name] = repo_kwargs
        api.write_config('repos', repo_config)
        core.echo('OK!')
        core.echo()


class RemoveRepo(core.CLI):
    '''Remove repo by name.'''

    name = 'remove'

    def setup_parser(self, parser):
        parser.add_argument(
            'name',
            help='Name of the repo',
        )

    def run(self, args):
        core.echo()
        if args.name in ['home', 'user', 'cwd']:
            core.echo('Error: Can not remove %s repo.' % args.name)

        repo_config = api.read_config('repos', {})
        if args.name not in repo_config:
            core.echo('Error: Repo named %s not found.' % args.name)
            core.exit(1)

        core.echo('- Removing repo from config...', end='')
        repo_config.pop(args.name)
        api.write_config('repos', repo_config)
        core.echo('OK!')
        core.echo()