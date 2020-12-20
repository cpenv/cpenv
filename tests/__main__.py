# -*- coding: utf-8 -*-

# Standard library imports
import subprocess
import sys


def main(*args):
    print('\n\nRunning Test Suite...\n\n')
    cmd = [
        'nosetests',
        '-v',
        '--logging-clear-handlers',
        '--with-coverage',
        '--cover-package=cpenv',
        '--exclude-dir=cpenv/vendor',
    ]
    sys.exit(subprocess.check_call(' '.join(cmd), shell=True))


if __name__ == '__main__':
    main(*sys.argv)
