# -*- coding: utf-8 -*-
import os


joinpath = os.path.join


def expandpath(path):
    '''Expand user and envvars in path.'''

    return os.path.expandvars(os.path.expanduser(path))


def unipath(*paths):
    '''Like os.path.join but also expands and normalizes path parts.'''

    return os.path.normpath(expandpath(joinpath(*paths)))
