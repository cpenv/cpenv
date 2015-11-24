import os
import sys


def main(*args):
    print('\n\nRunning Test Suite...\n\n')

    if 'cover' in args:
        cmd = 'nosetests -v --nocapture --with-coverage --cover-package=cpenv'
    else:
        cmd = 'nosetests -v --nocapture'

    os.system(cmd)


if __name__ == '__main__':
    main(*sys.argv)
