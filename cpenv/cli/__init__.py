import tqdm

from cpenv import repos
from cpenv.cli import (
    activate,
    clone,
    copy,
    core,
    create,
    edit,
    env,
    info,
    list,
    localize,
    publish,
    remove,
    repo,
    version,
)
from cpenv.reporter import Reporter


class CpenvCLI(core.CLI):
    """
    Create, activate and manage Modules.

    A Module is a folder containing a module.yml file describing the Module's
    name, version, requirements, and environment variables. Module's can also
    contain a hooks folder with python files that respond to specific events.
    """

    name = "cpenv"
    usage = "cpenv [-h] <command> [<args>...]"

    def commands(self):
        return [
            activate.Activate(self),
            clone.Clone(self),
            copy.Copy(self),
            create.Create(self),
            info.Info(self),
            edit.Edit(self),
            env.Env(self),
            list.List(self),
            localize.Localize(self),
            publish.Publish(self),
            remove.Remove(self),
            repo.Repo(self),
            version.Version(self),
        ]


class CliReporter(Reporter):
    def __init__(self):
        self._bars = {}

    def get_bar_style(self, desc, total, unit=None, unit_divisor=None, unit_scale=None):
        return {
            "desc": desc,
            "total": total,
            "bar_format": "  {desc} {bar} {n_fmt}/{total_fmt}",
            "unit": unit or "iB",
            "unit_divisor": unit_divisor or 1024,
            "unit_scale": unit_scale or True,
        }

    def start_resolve(self, requirements):
        core.echo("- Resolving requirements...")
        core.echo()

    def resolve_requirement(self, requirement, module_spec):
        core.echo("  %s - %s" % (module_spec.qual_name, module_spec.path))

    def end_resolve(self, resolved, unresolved):
        core.echo()
        if unresolved:
            core.echo("Error: Failed to resolve %s" % ", ".join(unresolved))

    def start_localize(self, module_specs):
        for spec in module_specs:
            if not isinstance(spec.repo, repos.LocalRepo):
                core.echo("- Localizing modules...")
                core.echo()
                return

    def end_localize(self, modules):
        core.echo()

    def start_progress(self, label, max_size, data):
        if "download" in label.lower():
            spec = data["module_spec"]
            core.echo("  Downloading %s from %s..." % (spec.qual_name, spec.repo.name))
            desc = spec.qual_name
        elif "upload" in label.lower():
            module = data["module"]
            to_repo = data["to_repo"]
            core.echo("  Uploading %s to %s..." % (module.qual_name, to_repo.name))
            desc = module.qual_name
        else:
            desc = label

        style = self.get_bar_style(
            desc,
            max_size,
            data.get("unit", None),
            data.get("unit_divisor", 1024),
            data.get("unit_scale", True),
        )
        self._bars[label] = tqdm.tqdm(**style)

    def update_progress(self, label, chunk_size, data):
        bar = self._bars.get(label, None)
        if bar:
            bar.update(chunk_size)

    def end_progress(self, label, data):
        bar = self._bars.pop(label, None)
        if bar:
            bar.close()
