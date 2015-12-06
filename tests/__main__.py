import os
import sys


def main(*args):
    print('\n\nRunning Test Suite...\n\n')

    if 'cover' in args:
        cmd = ('nosetests -v --logging-clear-handlers '
               '--with-coverage --cover-package=cpenv')
    else:
        cmd = 'nosetests -v --logging-clear-handlers'

    os.system(cmd)


if __name__ == '__main__':
    main(*sys.argv)
