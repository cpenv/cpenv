import os
from contextlib import contextmanager
from functools import partial

data_path = partial(os.path.join, os.path.dirname(__file__), 'data')


@contextmanager
def cwd(new_cwd):

    old_cwd = os.getcwd()

    try:
        os.chdir(new_cwd)
        yield
    except:
        raise
    finally:
        os.chdir(old_cwd)


def touch(filepath):

    with open(filepath, 'a') as f:
        os.utime(filepath, None)


def make_files(*filepaths):

    for filepath in filepaths:
        d = os.path.dirname(filepath)

        try:
            os.makedirs(d)
        except:
            pass

        touch(filepath)
