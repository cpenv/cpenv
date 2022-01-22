# -*- coding: utf-8 -*-

# Local imports
from cpenv import paths

from . import data_path
from .utils import make_files


def test_exclusive_walk_includes_prebuilt_pyc():
    '''Ensure exclusive_walk keeps prebuilt .pyc files'''

    source_files = [
        data_path('paths/source/A.pyc'),
        data_path('paths/source/A.py'),
        data_path('paths/source/subdir/B.pyc'),
        data_path('paths/source/subdir/B.py'),
        data_path('paths/source/C.pyc'),
        data_path('paths/source/subdir/D.pyc'),
        data_path('paths/source/__pycache__/E.pyc'),
    ]
    make_files(*source_files)

    walked_files = []
    for root, subdirs, files in paths.exclusive_walk(data_path('paths')):
        for file in files:
            walked_files.append(paths.normalize(root, file))

    expected_files = [
        data_path('paths/source/A.py'),
        data_path('paths/source/subdir/B.py'),
        data_path('paths/source/C.pyc'),
        data_path('paths/source/subdir/D.pyc'),
    ]

    assert set(expected_files) == set(walked_files)
