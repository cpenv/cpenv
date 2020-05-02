# -*- coding: utf-8 -*-

# Standard library imports
import os
from contextlib import contextmanager
import cpenv


@contextmanager
def cwd(new_cwd):

    old_cwd = os.getcwd()

    try:
        os.chdir(new_cwd)
        cpenv.update_repo(cpenv.LocalRepo('cwd', new_cwd))
        yield
    except Exception:
        raise
    finally:
        os.chdir(old_cwd)
        cpenv.update_repo(cpenv.LocalRepo('cwd', old_cwd))


def touch(filepath):

    with open(filepath, 'a'):
        os.utime(filepath, None)


def make_files(*filepaths, **kwargs):
    data = kwargs.get('text', None)

    for filepath in filepaths:
        d = os.path.dirname(filepath)

        try:
            os.makedirs(d)
        except Exception:
            pass

        if not data:
            touch(filepath)
        else:
            with open(filepath, 'w') as f:
                f.write(data)
