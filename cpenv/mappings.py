# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import collections
import os
import random
import sys
import tempfile
from string import Template
try:
    from collections.abc import Mapping, MutableMapping, Sequence
except ImportError:
    from collections import Mapping, MutableMapping, Sequence

# Local imports
from . import paths
from .compat import numeric_types, platform, supported_platforms, string_types
from .vendor import yaml


env_value_types = numeric_types + string_types
Item = collections.namedtuple('Item', 'key value')
Op = collections.namedtuple('Op', 'key value op')


class CaseInsensitiveDict(MutableMapping):
    '''A case insensitive dict that expects strings as keys.

    Based on the requests.structures.CaseInsensitiveDict.
    '''

    def __init__(self, *args, **kwargs):
        self._items = dict()
        self.update(*args, **kwargs)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, dict(self.items()))

    def __setitem__(self, key, value):
        self._items[key.lower()] = Item(key, value)

    def __getitem__(self, key):
        return self._items[key.lower()].value

    def __delitem__(self, key):
        del self._items[key.lower()]

    def __iter__(self):
        return (item.key for item in self._items.values())

    def __len__(self):
        return len(self._items)

    def __eq__(self, other):
        other_cmp = self._comparable_mapping(other)
        if other_cmp is None:
            return NotImplemented
        self_cmp = self._comparable_mapping(self)
        return self_cmp == other_cmp

    @classmethod
    def _comparable_mapping(cls, mapping):
        if isinstance(mapping, CaseInsensitiveDict):
            return {item.key.lower(): item.value for item in mapping.values()}
        if isinstance(mapping, Mapping):
            return {key.lower(): value for key, value in mapping.items()}


class EnvironmentDict(CaseInsensitiveDict):
    '''A dict suited to storing and manipulating environment variables.

    Lowercase comparisons are used to ensure unique keys and values.

    The following methods make it easy to build an Environment.
    - set: insert or overwrite the value of a key.
    - unset: discard a key.
    - remove: discard an item or list of items from a key's value.
    - append: add an item or list of items to the tail of a key's value.
    - prepend: add an item or list of items to the head of a key's value.

    Example:
        >>> env = EnvironmentDict()
        >>> env.append('PATH', '/some/path')
        >>> env.prepend('path', '/some/other/path')
        >>> env.remove('PATH', '/some/path')
        >>> assert env['PATH'] == ['/some/other/path']
    '''

    _value_error = 'Expected Union[list, Union[str, int, float]] got %s'

    def __init__(self, *args, **kwargs):
        self._add_condition = kwargs.pop('add_condition', ignore_case)
        super(EnvironmentDict, self).__init__(*args, **kwargs)

    def _get_list(self, key):
        value = self.get(key, None)
        if value is None:
            return []
        if isinstance(value, env_value_types):
            return [value]
        if isinstance(value, Sequence):
            return list(value)
        raise ValueError('%s could not be converted to a list.' % value)

    def _coerce_value(self, value):
        if isinstance(value, env_value_types):
            return str(value)
        elif isinstance(value, Sequence):
            result = []
            for v in value:
                if v in (None, ''):
                    continue
                result.append(str(value))
            return result
        else:
            raise ValueError(self._value_error % type(value))

    def _remove_condition(self, current_value, value):
        return not self._add_condition(current_value, value)

    def unset(self, key, value=None):
        '''Unset a key.'''

        self.pop(key, None)

    def set(self, key, value):
        '''Set a key.'''

        self[key] = self._coerce_value(value)

    def remove(self, key, value, remove_check=None):
        '''Remove a value from a key.'''

        value = self._coerce_value(value)

        if key not in self:
            return

        result = self._get_list(key)
        if isinstance(value, env_value_types):
            if self._remove_condition(result, value):
                result.remove(value)
        elif isinstance(value, Sequence):
            for v in value:
                if self._remove_condition(result, v):
                    result.remove(v)

        if not result:
            self.pop(key, None)
        else:
            self[key] = result

    def prepend(self, key, value, add_check=None):
        '''Prepend a value to a key.

        Sets the value if the key does not exist.
        '''

        result = self._get_list(key)
        value = self._coerce_value(value)

        if isinstance(value, env_value_types):
            if self._add_condition(result, value):
                result.insert(0, value)
        elif isinstance(value, Sequence):
            for v in value:
                if self._add_condition(result, v):
                    result.insert(0, v)

        self[key] = result

    def append(self, key, value, add_check=None):
        '''Append a value to a key.

        Sets the value if the key does not exist.
        '''

        result = self._get_list(key)
        value = self._coerce_value(value)

        if isinstance(value, env_value_types):
            if self._add_condition(result, value):
                result.append(value)
        elif isinstance(value, Sequence):
            for v in value:
                if self._add_condition(result, v):
                    result.append(v)

        self[key] = result


class EnvironmentDictTokenizer(object):
    '''Responsible for converting a dict into a list of Operation tokens that
    can be used to merge one dict with another. Used internally by
    `join_dicts`.

    An Op token will be returned for each of the following keys:
    - set: insert or overwrite the value of a key.
    - unset: discard a key.
    - remove: discard an item or list of items from a key's value.
    - append: add an item or list of items to the tail of a key's value.
    - prepend: add an item or list of items to the head of a key's value.

    You may specify platform specific keys, the value of the current platform
    will be extracted before tokenization.
    - win
    - osx
    - linux

    Example:
        >>> data = {
        ...     'PATH': [
        ...         {'append': '/path/a'},
        ...         {'remove': ['/path/b', '/path/c']}
        ...     ],
        ... }
        [Op('PATH', '/path/a', 'append'), Op('PATH', '/path/b', 'remove')...]
    '''

    operation_names = ['unset', 'set', 'remove', 'append', 'prepend']

    @staticmethod
    def _is_explicit_list_value(value):
        return len(value) and isinstance(value[0], Mapping)

    @classmethod
    def tokenize_mapping(cls, key, value, op, tokens):
        # Handle platform specific keys
        for plat in supported_platforms:
            if plat in value:
                if platform == 'mac':
                    # mac and osx are valid platform keys for macos
                    plat_value = value.get(platform, value.get('osx', None))
                else:
                    plat_value = value.get(platform, None)
                if plat_value:
                    cls.tokenize_value(key, plat_value, op, tokens)
                return

        # Handle explicit operations keys
        for op, op_value in value.items():
            if op not in cls.operation_names:
                raise KeyError('Invalid key in dict value: %s' % op)
            cls.tokenize_value(key, op_value, op, tokens)

    @classmethod
    def tokenize_str(cls, key, value, op, tokens):
        if isinstance(value, bool):
            value = str(int(value))
        elif isinstance(value, env_value_types):
            value = str(value)
        elif value is None:
            # Skip null values
            return
        else:
            raise ValueError('Got invalid value %s for key %s' % (value, key))
        tokens.append(Op(key, value, op))

    @classmethod
    def tokenize_sequence(cls, key, value, op, tokens):
        if not cls._is_explicit_list_value(value) and op == 'prepend':
            value = value[::-1]

        for item in value:
            cls.tokenize_value(key, item, op, tokens)

    @classmethod
    def tokenize_value(cls, key, value, op=None, tokens=None):
        if tokens is None:
            tokens = []
        if op == 'set':
            tokens.append(Op(key, None, 'unset'))
        if isinstance(value, env_value_types):
            op = op or 'set'
            cls.tokenize_str(key, value, op, tokens)
        elif isinstance(value, Mapping):
            op = op or 'set'
            cls.tokenize_mapping(key, value, op, tokens)
        elif isinstance(value, Sequence):
            if op in (None, 'set'):
                op = 'prepend'
            cls.tokenize_sequence(key, value, op, tokens)
        else:
            raise ValueError('Could not tokenize %s' % value)

        return tokens

    @classmethod
    def tokenize(cls, data):
        tokens = []
        for key, value in data.items():
            tokens.extend(cls.tokenize_value(key, value))
        return tokens


def ignore_case(items, value):
    '''Default add_condition for `EnvironmentDict`.

    Returns True if value is not in items.
    '''

    return value.lower() not in [item.lower() for item in items]


def tokenize_dict(data):
    '''Tokenize a dict returning a list of Ops that can be used to
    join the dict with another.
    '''

    return EnvironmentDictTokenizer.tokenize(data)


def join_dicts(*dicts, **kwargs):
    '''Join a bunch of dicts.

    Arguments:
        *dicts: Dictionaries to merge
        add_condition (fn): Used to check if a value should be added to a key
    '''

    env_dict = EnvironmentDict(**kwargs)
    for data in dicts:
        tokens = tokenize_dict(data)
        for token in tokens:
            if token.op == 'unset':
                env_dict.unset(token.key, token.value)
            elif token.op == 'set':
                env_dict.set(token.key, token.value)
            elif token.op == 'remove':
                env_dict.remove(token.key, token.value)
            elif token.op == 'prepend':
                env_dict.prepend(token.key, token.value)
            elif token.op == 'append':
                env_dict.append(token.key, token.value)
    return dict(env_dict)


def env_to_dict(env, pathsep=os.pathsep):
    '''
    Convert a dict containing environment variables into a standard dict.
    Variables containing multiple values will be split into a list based on
    the argument passed to pathsep.

    :param env: Environment dict like dict(os.environ)
    :param pathsep: Path separator used to split variables
    '''

    out_dict = {}

    for k, v in env.items():
        if pathsep in v:
            out_dict[k] = v.split(pathsep)
        else:
            out_dict[k] = v

    return out_dict


def dict_to_env(d, pathsep=os.pathsep):
    '''
    Convert a python dict to a dict containing valid environment variable
    values.

    :param d: Dict to convert to an env dict
    :param pathsep: Path separator used to join lists(default os.pathsep)
    '''

    out_env = {}

    for k, v in d.items():
        if isinstance(v, list):
            out_env[k] = pathsep.join(v)
        elif isinstance(v, string_types):
            out_env[k] = v
        else:
            raise TypeError('{} not a valid env var type'.format(type(v)))

    return out_env


def expand_envvars(env):
    '''
    Expand all environment variables in an environment dict

    :param env: Environment dict
    '''

    out_env = {}

    for k, v in env.items():
        out_env[k] = Template(v).safe_substitute(env)

    # Expand twice to make sure we expand everything we possibly can
    for k, v in out_env.items():
        out_env[k] = Template(v).safe_substitute(out_env)

    return out_env


def get_store_env_tmp():
    '''Returns an unused random filepath.'''

    tempdir = tempfile.gettempdir()
    temp_name = 'envstore{0:0>3d}'
    temp_path = paths.normalize(
        tempdir,
        temp_name.format(random.getrandbits(9))
    )
    if not os.path.exists(temp_path):
        return temp_path
    else:
        return get_store_env_tmp()


def store_env(path=None):
    '''Encode current environment as yaml and store in path or a temporary
    file. Return the path to the stored environment.
    '''

    path = path or get_store_env_tmp()

    env_dict = yaml.safe_dump(dict(os.environ), default_flow_style=False)

    with open(path, 'w') as f:
        f.write(env_dict)

    return path


def restore_env(env_dict):
    '''Set environment variables in the current python process from a dict
    containing envvars and values.'''

    if hasattr(sys, 'real_prefix'):
        sys.prefix = sys.real_prefix
        del(sys.real_prefix)

    replace_osenviron(expand_envvars(dict_to_env(env_dict)))


def restore_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.safe_load(f.read())

    restore_env(env_dict)


def set_env(*env_dicts):
    '''Set environment variables in the current python process from a dict
    containing envvars and values.'''

    old_env_dict = env_to_dict(dict(os.environ))
    new_env_dict = join_dicts(old_env_dict, *env_dicts)
    new_env = dict_to_env(new_env_dict)
    replace_osenviron(expand_envvars(new_env))


def set_env_from_file(env_file):
    '''Restore the current environment from an environment stored in a yaml
    yaml file.

    :param env_file: Path to environment yaml file.
    '''

    with open(env_file, 'r') as f:
        env_dict = yaml.safe_load(f.read())

    if 'environment' in env_dict:
        env_dict = env_dict['environment']

    set_env(env_dict)


def replace_osenviron(env_dict):
    for k in os.environ.keys():
        if k not in env_dict:
            del os.environ[k]

    for k, v in env_dict.items():
        os.environ[k] = v
