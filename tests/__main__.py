# -*- coding: utf-8 -*-

# Standard library imports
import subprocess
import sys


def main(*args):
    cmd = [
        'pytest',
        '-vv',
        '--cov=cpenv',
    ]
    sys.exit(subprocess.check_call(' '.join(cmd), shell=True))


if __name__ == '__main__':
    main(*sys.argv)
