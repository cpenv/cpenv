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

    with open(filepath, 'a'):
        os.utime(filepath, None)


def make_files(*filepaths, **kwargs):
    data = kwargs.get('data', None)

    for filepath in filepaths:
        d = os.path.dirname(filepath)

        try:
            os.makedirs(d)
        except:
            pass

        if not data:
            touch(filepath)
        else:
            with open(filepath, 'w') as f:
                f.write(data)
