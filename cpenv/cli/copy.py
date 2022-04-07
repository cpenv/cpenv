from cpenv import api
from cpenv.cli import core
from cpenv.resolver import Copier, Resolver


class Copy(core.CLI):
    """Copy Modules from one Repo to another."""

    def setup_parser(self, parser):
        parser.add_argument(
            "modules",
            help="Space separated list of modules.",
            nargs="+",
        )
        parser.add_argument(
            "--from_repo",
            help="Download from",
            default=None,
        )
        parser.add_argument(
            "--to_repo",
            help="Upload to",
            default=None,
        )
        parser.add_argument(
            "--overwrite",
            help="Overwrite the destination directory. (False)",
            action="store_true",
        )

    def run(self, args):

        core.echo()

        if args.from_repo:
            from_repo = api.get_repo(args.from_repo)
        else:
            from_repo = core.prompt_for_repo(
                api.get_repos(),
                "Download from",
                default_repo_name="home",
            )

        if args.to_repo:
            to_repo = api.get_repo(args.to_repo)
        else:
            repos = api.get_repos()
            repos.remove(from_repo)
            to_repo = core.prompt_for_repo(
                repos,
                "Upload to",
                default_repo_name="home",
            )

        resolver = Resolver([from_repo])
        module_specs = resolver.resolve(args.modules)
        core.echo()

        choice = core.prompt("Copy these modules to %s?[y/n] " % to_repo.name)
        if choice.lower() not in ["y", "yes", "yup"]:
            core.echo("Aborted.")
            core.exit(1)
        core.echo()

        copier = Copier(to_repo)
        copier.copy(module_specs, args.overwrite)
