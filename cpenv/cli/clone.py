import os
import sys

from cpenv import api, paths, shell
from cpenv.cli import core
from cpenv.resolver import ResolveError


class Clone(core.CLI):
    """
    Clone a Module for development.

    The following repos are available by default:
        home - Local repo pointing to a computer-wide cpenv directory
        user - Local repo pointing to a user-specific cpenv directory

    For a full listing of available repos use the repo cli command:
        cpenv repo list
    """

    def setup_parser(self, parser):
        parser.add_argument(
            "module",
            help="Module to clone.",
        )
        parser.add_argument(
            "where",
            help="Destination directory. (./<module_name>)",
            nargs="?",
            default=None,
        )
        parser.add_argument(
            "--from_repo",
            help="Specific repo to clone from.",
            default=None,
        )
        parser.add_argument(
            "--overwrite",
            help="Overwrite the destination directory. (False)",
            action="store_true",
        )

    def run(self, args):

        try:
            if not args.from_repo:
                module_spec = api.resolve([args.module])[0]
            else:
                from_repo = api.get_repo(args.from_repo)
                module_spec = from_repo.find(args.module)[0]
        except Exception:
            core.echo()
            core.echo("Error: Failed to resolve " + args.module)
            core.exit(1)

        where = paths.normalize(args.where or ".", module_spec.real_name)
        if os.path.isdir(where):
            core.echo("Error: Directory already exists - " + where)
            core.exit(1)

        core.echo("- Cloning %s..." % module_spec.real_name)
        core.echo()
        try:
            module = module_spec.repo.download(
                module_spec,
                where=where,
                overwrite=args.overwrite,
            )
        except Exception as e:
            core.echo()
            core.echo("Error: " + str(e))
            core.exit(1)

        core.echo()
        core.echo("Navigate to the following folder to make changes:")
        core.echo("  " + module.path)
        core.echo()
        core.echo("Use one of the following commands to publish your changes:")
        core.echo("  cpenv publish .")
        core.echo('  cpenv publish . --to_repo="repo_name"')
