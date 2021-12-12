from cpenv import api
from cpenv.cli import core
from cpenv.module import best_match


class Remove(core.CLI):
    '''Permanently remove a Module from a Repo.'''

    def setup_parser(self, parser):
        parser.add_argument(
            'modules',
            help='Space separated list of modules.',
            nargs='+',
        )
        parser.add_argument(
            '--from_repo',
            help='Specific repo to remove from.',
            default=None,
        )

    def run(self, args):

        core.echo()

        if args.from_repo:
            from_repo = api.get_repo(name=args.from_repo)
        else:
            from_repo = core.prompt_for_repo(
                api.get_repos(),
                'Choose a repo to remove module from',
                default_repo_name='home',
            )

        core.echo('- Finding modules in %s...' % from_repo.name)
        core.echo()
        modules_to_remove = []
        for requirement in args.modules:
            module = best_match(requirement, from_repo.find(requirement))
            if not module:
                core.echo('Error: %s not found...' % requirement)
                core.exit(1)
            core.echo('  %s - %s' % (module.real_name, module.path))
            modules_to_remove.append(module)

        core.echo()
        choice = core.prompt('Delete these modules?[y/n] ')
        if choice.lower() not in ['y', 'yes', 'yup']:
            core.echo('Aborted.')
            core.exit(1)

        core.echo()
        core.echo('- Removing modules...')
        core.echo()
        for module in modules_to_remove:
            core.echo('  ' + module.real_name)
            api.remove(module, from_repo)

        core.echo()
        core.echo('Successfully removed modules.')
        core.echo()
