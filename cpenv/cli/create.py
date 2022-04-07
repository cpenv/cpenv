import os

from cpenv import api, paths
from cpenv.cli import core
from cpenv.module import parse_module_path


class Create(core.CLI):
    """Create a new Module."""

    def setup_parser(self, parser):
        parser.add_argument(
            "where",
            help="Path to new module",
        )

    def run(self, args):
        where = paths.normalize(args.where)
        if os.path.isdir(where):
            core.echo()
            core.echo("Error: Can not create module in existing directory.")
            core.exit(1)

        default_name, default_version = parse_module_path(where)

        core.echo()
        core.echo("This command will guide you through creating a new module.")
        core.echo()
        name = core.prompt("  Module Name [%s]: " % default_name)
        version = core.prompt("  Version [%s]: " % default_version.string)
        description = core.prompt("  Description []: ")
        author = core.prompt("  Author []: ")
        email = core.prompt("  Email []: ")

        core.echo()
        core.echo("- Creating your new Module...", end="")
        module = api.create(
            where=where,
            name=name or default_name,
            version=version or default_version.string,
            description=description,
            author=author,
            email=email,
        )
        core.echo("OK!")

        core.echo()
        core.echo("  " + module.path)

        core.echo()
        core.echo("Steps you might take before publishing...")
        core.echo()
        core.echo("  - Include binaries your module depends on")
        core.echo("  - Edit the module.yml file")
        core.echo("    - Add variables to the environment section")
        core.echo("    - Add other modules to the requires section")
        core.echo("  - Add python hooks like post_activate")
        core.echo()
