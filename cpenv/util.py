# -*- coding: utf-8 -*-
import os


def expandpath(path):
    '''Expand user and envvars in path.'''

    return os.path.expandvars(os.path.expanduser(path))


def unipath(*paths):
    '''Like os.path.join but also expands and normalizes path parts.'''

    return os.path.normpath(expandpath(os.path.join(*paths)))


def binpath(*paths):
    '''Like os.path.join but acts relative to this packages bin path.'''

    return os.path.normpath(os.path.join(os.path.dirname(__file__), *paths))
