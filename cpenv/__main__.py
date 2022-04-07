import atexit
import sys

from cpenv import api, cli, reporter
from cpenv.cli import core


def perform_self_version_check():
    from cpenv import _self_version_check

    is_latest, current, latest = _self_version_check.is_latest_version()
    if not is_latest:
        _self_version_check.warn_newer_version_available(current, latest)


def main():
    atexit.register(perform_self_version_check)
    reporter.set_reporter(cli.CliReporter())
    core.run(cli.CpenvCLI, sys.argv[1:])


if __name__ == "__main__":
    main()
