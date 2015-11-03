# -*- coding: utf-8 -*-

import os

package_root = os.path.dirname(__file__)


def expandpath(path):
    '''Expand user and envvars in path.'''

    return os.path.expandvars(os.path.expanduser(path))


def unipath(*paths):
    '''Like os.path.join but also expands and normalizes path parts.'''

    return os.path.normpath(expandpath(os.path.join(*paths)))


def binpath(*paths):
    '''Like os.path.join but acts relative to this packages bin path.'''

    return os.path.normpath(os.path.join(package_root, 'bin', *paths))


def walk_dn(start_dir, depth=10):
    '''Walk down a directory tree. Same as os.walk but allows for a depth limit
    via depth argument'''

    start_depth = len(os.path.split(start_dir))
    end_depth = start_depth + depth

    for root, subdirs, files in os.walk(start_dir):
        yield root, subdirs, files

        if len(os.path.split(root)) >= end_depth:
            break
