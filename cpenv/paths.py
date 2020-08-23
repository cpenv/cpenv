# -*- coding: utf-8 -*-
'''
Tools for working with paths and files.
'''

# Standard library imports
from fnmatch import fnmatch
import os
import shutil
import stat
import zipfile


def normalize(*parts):
    '''Join, expand, and normalize a filepath.'''

    path = os.path.expanduser(os.path.expandvars(os.path.join(*parts)))
    return os.path.abspath(path).replace('\\', '/')


def parent(path):
    '''Get a file paths parent directory'''
    return normalize(os.path.dirname(path))


def ensure_path_exists(path, *args):
    '''Like os.makedirs but keeps quiet if path already exists'''

    if os.path.exists(path):
        return

    os.makedirs(path, *args)


def rmtree(path):
    '''Safely remove directory and all of it's contents.'''

    def onerror(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(path, onerror=onerror)


def walk_up(start_dir, depth=20):
    '''Walk up a directory tree'''
    root = start_dir

    for i in range(depth):
        contents = os.listdir(root)
        subdirs, files = [], []
        for f in contents:
            if os.path.isdir(os.path.join(root, f)):
                subdirs.append(f)
            else:
                files.append(f)

        yield root, subdirs, files

        parent = os.path.dirname(root)
        if parent and not parent == root:
            root = parent
        else:
            break


def touch(filepath):
    '''Touch the given filepath'''

    with open(filepath, 'a'):
        os.utime(filepath, None)


def format_size(bytesize):
    '''Human readable size.'''

    value = bytesize
    for unit in ['b', 'kb', 'mb', 'gb', 'tb', 'pb', 'zi']:
        if value < 1024.0:
            return "{:.0f} {}".format(value, unit)
        value /= 1024.0
    return "{:.0f} {}".format(value, unit)


def get_file_count(folder):
    '''Get the number of files in a folder.'''

    count = 0
    for _, _, files in exclusive_walk(folder):
        count += len(files)
    return count


def get_folder_size(folder):
    '''Get the size of a folder in bytes.'''

    size = 0
    for root, _, files in exclusive_walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path):
                size += os.path.getsize(file_path)
    return size


def is_excluded(value, exclude, exclude_patterns):
    '''Check if a string value matches exclude values and glob patterns'''

    return (
        value in exclude
        or any([fnmatch(value, p) for p in exclude_patterns])
    )


def exclusive_walk(folder, exclude=None, exclude_patterns=None):
    '''Like os.walk but exclude files by value or glob pattern.'''

    exclude = exclude or ['__pycache__', '.git', 'thumbs.db', '.venv', 'venv']
    exclude_patterns = exclude_patterns or ['*.pyc', '*.egg-info']

    for root, subdirs, files in os.walk(folder):
        if is_excluded(os.path.basename(root), exclude, exclude_patterns):
            subdirs[:] = []
            continue

        included = []
        for file in files:
            if is_excluded(file, exclude, exclude_patterns):
                continue
            included.append(file)

        yield root, subdirs, included


def zip_folder(folder, where):
    '''Zip the contents of a folder.'''

    parent = os.path.dirname(where)
    if not os.path.isdir(parent):
        os.makedirs(parent)

    # TODO: Count files first so we can report progress of building zip.

    with zipfile.ZipFile(where, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, subdirs, files in paths.exclusive_walk(folder):
            rel_root = os.path.relpath(root, folder)
            for file in files:
                zip_file.write(
                    os.path.join(root, file),
                    arcname=os.path.join(rel_root, file)
                )
