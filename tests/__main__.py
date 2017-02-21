# -*- coding: utf-8 -*-

import os
import sys


def main(*args):
    print('\n\nRunning Test Suite...\n\n')
    cmd = 'nosetests -v --logging-clear-handlers --with-coverage --cover-package=cpenv'
    os.system(cmd)


if __name__ == '__main__':
    main(*sys.argv)
