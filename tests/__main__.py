# -*- coding: utf-8 -*-

import sys
import subprocess


def main(*args):
    print('\n\nRunning Test Suite...\n\n')
    cmd = 'nosetests -v --logging-clear-handlers --with-coverage --cover-package=cpenv'
    sys.exit(subprocess.check_call(cmd, shell=True))


if __name__ == '__main__':
    main(*sys.argv)
