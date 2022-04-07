from cpenv import api
from cpenv.cli import core
from cpenv.repos import LocalRepo
from cpenv.resolver import Localizer, ResolveError


class Localize(core.CLI):
    """Localize a list of Modules.

    Downloads modules from a remote Repo and places them in the home LocalRepo
    by default. Use the --to_repo option to specify a LocalRepo.
    """

    def setup_parser(self, parser):
        parser.add_argument(
            "modules",
            help="Space separated list of modules.",
            nargs="+",
        )
        parser.add_argument(
            "--to_repo",
            "-r",
            help="Specific repo to localize to. (first match)",
            default=None,
        )
        parser.add_argument(
            "--overwrite",
            "-o",
            help="Overwrite the destination directory. (False)",
            action="store_true",
        )

    def run(self, args):

        core.echo()

        if args.to_repo:
            to_repo = api.get_repo(name=args.to_repo)
        else:
            repos = [r for r in api.get_repos() if isinstance(r, LocalRepo)]
            to_repo = core.prompt_for_repo(
                repos,
                "Choose a repo to localize to",
                default_repo_name="home",
            )

        # Resolve modules
        try:
            resolved = api.resolve(args.modules)
        except ResolveError:
            core.exit(1)

        # Localize modules from remote repos
        remote_modules = [
            spec for spec in resolved if not isinstance(spec.repo, LocalRepo)
        ]

        if not len(remote_modules):
            core.echo("All modules are already local...")
            core.exit()

        try:
            localizer = Localizer(to_repo)
            localizer.localize(
                remote_modules,
                overwrite=args.overwrite,
            )
        except Exception as e:
            core.echo("Error: " + str(e))
            core.exit(1)
