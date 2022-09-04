# -*- coding: utf-8 -*-
"""
Tools for working with paths and files.
"""

# Standard library imports
import os
import shutil
import stat
import zipfile
from fnmatch import fnmatch


def normalize(*parts):
    """Join, expand, and normalize a filepath."""

    path = os.path.expanduser(os.path.expandvars(os.path.join(*parts)))
    return os.path.abspath(path).replace("\\", "/")


def parent(path):
    """Get a file paths parent directory"""
    return normalize(os.path.dirname(path))


def ensure_path_exists(path, *args):
    """Like os.makedirs but keeps quiet if path already exists"""

    if os.path.exists(path):
        return

    os.makedirs(path, *args)


def is_writable(path):
    """Check if a directory is writable."""

    if os.path.exists(path):
        return os.access(path, os.X_OK | os.W_OK)

    try:
        os.makedirs(path)
        touch(normalize(path, "tmpfile"))
    except OSError as e:
        return False
    else:
        rmtree(path)
        return True


def rmtree(path):
    """Safely remove directory and all of it's contents."""

    def onerror(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(path, onerror=onerror)


def walk_up(start_dir, depth=20):
    """Like os.walk but walks up a tree."""

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
    """Touch the given filepath"""

    with open(filepath, "a"):
        os.utime(filepath, None)


def format_size(bytesize):
    """Human readable size."""

    value = bytesize
    for unit in ["b", "kb", "mb", "gb", "tb", "pb", "zi"]:
        if value < 1024.0:
            return "{:.0f} {}".format(value, unit)
        value /= 1024.0
    return "{:.0f} {}".format(value, unit)


def get_file_count(folder):
    """Get the number of files in a folder."""

    count = 0
    for _, _, files in exclusive_walk(folder):
        count += len(files)
    return count


def get_folder_size(folder):
    """Get the size of a folder in bytes."""

    size = 0
    for root, _, files in exclusive_walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path):
                size += os.path.getsize(file_path)
    return size


def exclude_names(names):
    """Returns True when a file matches one of the provided names."""

    def check_file_against_names(file):
        return os.path.basename(file) in names

    return check_file_against_names


def exclude_patterns(patterns):
    """Returns True when a file matches against one of the provided patterns"""

    def check_file_against_patterns(file):
        return any([fnmatch(file, p) for p in patterns])

    return check_file_against_patterns


def include_prebuilt_pyc(file):
    """Returns True when a pyc file has no accompanying py file.

    This is useful in cases where tool distributors prebuild pyc files as
    a crude form of anti-piracy. These need to be included in cpenv modules
    when zipped to be uploaded to a repository.
    """

    return (
        file.endswith(".pyc")
        and not os.path.isfile(file.replace(".pyc", ".py"))
        and "__pycache__" not in file
    )


def is_excluded(value, predicates):
    """Check if a value matches any of the exclude predicates."""

    return any([predicate(value) for predicate in predicates])


def is_included(value, predicates):
    """Returns True if value matches any of the include predicates."""

    return any([predicate(value) for predicate in predicates])


def exclusive_walk(folder, excludes=None, includes=None):
    """Like os.walk but excludes/includes files by using predicate functions.

    Excludes the following by default:
        names: __pycache__, .git, Thumbs.db, .venv, venv
        patterns: *.pyc, *.egg-info

    Includes the following by default:
        .pyc files that have no accompanying .py file.

    Arguments:
        folder (str): Root folder to recursively walk.
        excludes ([callable]): List of predicate functions used to exclude files.
        includes ([callable]): List of predicate functions to include files. Overrides excludes.

    Returns:
        Generator yielding (root, subdirs, files).
    """

    excludes = excludes or [
        exclude_names(["__pycache__", ".git", "thumbs.db", ".venv", "venv"]),
        exclude_patterns(["*.pyc", "*.egg-info"]),
    ]
    includes = includes or [include_prebuilt_pyc]

    for root, subdirs, files in os.walk(folder):
        if is_excluded(root, excludes) and not is_included(root, includes):
            subdirs[:] = []
            continue

        included_files = []
        for file in files:
            path = normalize(root, file)
            if is_excluded(path, excludes) and not is_included(path, includes):
                continue
            included_files.append(file)

        yield root, subdirs, included_files


def get_folder_info(folder):
    """Get info about a folder and it's contents.

    Returns:
        A dict containing the size, file count, and list of files in, a folder.
    """

    info = {
        "size": 0,
        "file_count": 0,
        "files": [],
    }
    for root, subdirs, files in exclusive_walk(folder):
        rel_root = os.path.relpath(root, folder)
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.join(rel_root, file)
            info["size"] += os.path.getsize(file_path)
            info["file_count"] += 1
            info["files"].append((file_path, rel_path))
    return info


def zip_folder_from_info(info, where, progress_cb=None):
    """Zips a folder using info provided by `get_folder_info`."""

    parent = os.path.dirname(where)
    if not os.path.isdir(parent):
        os.makedirs(parent)

    with zipfile.ZipFile(where, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for full_path, rel_path in info["files"]:
            zip_file.write(full_path, arcname=rel_path)
            if progress_cb:
                progress_cb(1)


def zip_folder(folder, where):
    """Zip the contents of a folder."""

    parent = os.path.dirname(where)
    if not os.path.isdir(parent):
        os.makedirs(parent)

    # TODO: Count files first so we can report progress of building zip.

    with zipfile.ZipFile(where, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, subdirs, files in exclusive_walk(folder):
            rel_root = os.path.relpath(root, folder)
            for file in files:
                zip_file.write(
                    os.path.join(root, file), arcname=os.path.join(rel_root, file)
                )
