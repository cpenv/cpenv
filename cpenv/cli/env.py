import argparse
import re

from cpenv import api
from cpenv.cli import core


class Env(core.CLI):
    '''
    Manage, Configure and list Repos.

    Repos are sources of Modules. A Repo can be local or remote. Modules
    stored in remote Repos will be localized to a local repo prior to
    activation or explicitly by using "cpenv localize".
    '''

    def commands(self):
        return [
            ListEnv(self),
            SaveEnv(self),
            RemoveEnv(self),
        ]


class ListEnv(core.CLI):
    '''
    List available Environments.

    Environments are like Aliases for a list of module requirements. They
    can be Activated using a single name rather than providing a full list of
    module requirements.
    '''

    name = 'list'

    def setup_parser(self, parser):
        parser.add_argument(
            'filters',
            help='Environment filters like --name="My*".',
            nargs=argparse.REMAINDER,
        )

    def parse_filters(self, filters):
        pattern = (
            r'-{1,2}(?P<param>[a-zA-Z0-9_]+)=*\s*'
            r'"?(?P<value>.+)"?'
        )
        kwargs = {}
        for arg in filters:
            match = re.search(pattern, arg)
            param = match.group('param')
            raw_value = '"%s"' % match.group('value').strip()
            value = core.safe_eval(raw_value)
            kwargs[param] = value
        return kwargs

    def run(self, args):

        filters = self.parse_filters(args.filters)
        core.echo()

        found_environments = False

        for repo in api.get_repos():
            environments = repo.list_environments(filters)
            env_names = sorted([env.name for env in environments])
            if env_names:
                found_environments = True
                if repo.name != repo.path:
                    header = repo.name + ' - ' + repo.path
                else:
                    header = repo.name
                core.echo(core.format_columns(
                    header,
                    env_names,
                    indent='  ',
                ))
                core.echo()

        if not found_environments:
            core.echo('No Environments are were found.')
            core.echo('Use "cpenv env save <name>" to save an Environment.')


class SaveEnv(core.CLI):
    '''
    Save an Environment.

    Examples:
        cpenv env save my_env
        cpenv env save --force my_env
        cpenv env save --no_versions my_env
        cpenv env save --repo MyShotgunRepo --project=1234 my_env
    '''

    name = 'save'

    def setup_parser(self, parser):
        parser.add_argument(
            '--repo',
            help='Repo to save the Environment in.',
            default='home',
        )
        parser.add_argument(
            '--force',
            help='Overwrite existing Environment? (False)',
            action='store_true',
        )
        parser.add_argument(
            '--no_versions',
            help='Write requirements without versions. (False)',
            action='store_true',
        )
        parser.add_argument(
            'name',
            help='Name of the Environment.'
        )
        parser.add_argument(
            'data',
            help='Data to include in Environment.',
            nargs=argparse.REMAINDER,
        )

    def parse_data(self, data):
        pattern = (
            r'-{1,2}(?P<param>[a-zA-Z0-9_]+)=*\s*'
            r'"?(?P<value>.+)"?'
        )
        kwargs = {}
        for arg in data:
            match = re.search(pattern, arg)
            param = match.group('param')
            raw_value = '"%s"' % match.group('value').strip()
            value = core.safe_eval(raw_value)
            kwargs[param] = value
        return kwargs

    def run(self, args):

        extra_data = self.parse_data(args.data)
        repo = api.get_repo(args.repo)
        requires = api.get_active_modules()

        if not requires:
            core.echo('Activate some modules before you save an Environment.')
            return

        if args.no_versions:
            requires = [m.name for m in requires]
        else:
            requires = [m.qual_name for m in requires]

        data = {
            'name': args.name,
            'requires': requires,
        }
        data.update(extra_data)

        repo.save_environment(
            name=data['name'],
            data=data,
            force=args.force,
        )


class RemoveEnv(core.CLI):
    '''
    Remove an Environment.

    Examples:
      cpenv env remove my_env
      cpenv env remove my_env --from_repo SomeRepo
    '''

    name = 'remove'

    def setup_parser(self, parser):
        parser.add_argument(
            'name',
            help='Name of the Environment.'
        )
        parser.add_argument(
            '--from_repo',
            help='Repo to remove the Environment from.',
            default='home',
        )

    def run(self, args):

        name = args.name
        from_repo = api.get_repo(name=args.from_repo)

        core.echo()
        core.echo('- Removing Environment from %s...' % from_repo.name)
        core.echo()

        env_removed = False
        for env in from_repo.list_environments():
            if env.name == name:
                env_removed = True
                from_repo.remove_environment(env.name)

        if env_removed:
            core.echo('Successfully removed %s.' % name)
        else:
            core.echo('Could not find Environment "%s".' % name)

        core.echo()
