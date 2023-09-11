from cpenv import api
from cpenv.cli import core
from cpenv.module import Module
from cpenv.resolver import Resolver


class Publish(core.CLI):
    """Publish a Module to a repo."""

    def setup_parser(self, parser):
        parser.add_argument(
            "module",
            help='Path of module to publish. (".")',
            default=".",
            nargs="?",
        )
        parser.add_argument(
            "--to_repo",
            help="Specific repo to clone from.",
            default=None,
        )
        parser.add_argument(
            "--overwrite",
            help="Overwrite the destination directory. (False)",
            action="store_true",
        )

    def run(self, args):
        core.echo()

        # Get repo
        if args.to_repo:
            to_repo = api.get_repo(name=args.to_repo)
        else:
            to_repo = core.prompt_for_repo(
                api.get_repos(),
                "Choose a repo to publish to",
                default_repo_name="home",
            )

        # Resolve module
        resolver = Resolver(api.get_repos())
        module_spec = resolver.resolve([args.module])[0]
        core.echo()

        # Confirm publication
        choice = core.prompt("Publish module to %s?[y/n] " % to_repo.name)
        if choice.lower() not in ["y", "yes", "yup"]:
            core.echo("Aborted.")
            core.exit(1)

        # Publish
        module = Module(module_spec.path)
        try:
            published = to_repo.upload(module, args.overwrite)
        except Exception as e:
            core.echo()
            core.echo("{}: {}".format(type(e).__name__, e))
            return

        core.echo()
        core.echo("Activate your module:")
        core.echo("  cpenv activate %s" % published.qual_name)
        core.echo()
