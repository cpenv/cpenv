import os
import sys

from cpenv import api, repos, shell
from cpenv.resolver import ResolveError
from cpenv.cli import core


class Edit(core.CLI):
    '''Open a module in a text editor.

    Editor Lookup:
        1. CPENV_EDITOR environment variable
        2. EDITOR environment variable
        3. subl (default editor)
    '''

    usage = 'cpenv edit [-h, --env] <module_or_environment>'

    def setup_parser(self, parser):
        parser.add_argument(
            '--env',
            help='Edit an Environment instead of a Module.',
            action='store_true',
        )
        parser.add_argument(
            'module_or_environment',
            help='Module or Environment name.',
        )

    def run(self, args):
        core.echo()
        if args.env:
            return self.run_env(args.module_or_environment)

        try:
            module_spec = api.resolve([args.module_or_environment])[0]
        except ResolveError:
            sys.exit(1)

        if not isinstance(module_spec.repo, repos.LocalRepo):
            core.echo('%s - %s' % (module_spec.qual_name, module_spec.path))
            core.echo('Error: Can only edit modules in local repositories.')
            sys.exit(1)

        editor = os.getenv('CPENV_EDITOR', os.getenv('EDITOR', 'subl'))
        core.echo('Opening %s in %s.' % (module_spec.path, editor))
        shell.run(editor, module_spec.path)

    def run_env(self, environment):
        file = None
        repo = False
        found_in_remote = False
        for repo in api.get_repos():
            for env in repo.list_environments():
                if env.name == environment:
                    if isinstance(repo, repos.LocalRepo):
                        file = env.path
                        break
                    else:
                        repo = repo
                        found_in_remote = True
            if file:
                break

        if found_in_remote:
            core.echo('Error: Can only edit Environments in local repos.')
            core.echo('Found %s in repo %s' % (environment, repo.name))
            sys.exit(1)

        editor = os.getenv('CPENV_EDITOR', os.getenv('EDITOR', 'subl'))
        core.echo('Opening %s in %s.' % (file, editor))
        shell.run(editor, file)
