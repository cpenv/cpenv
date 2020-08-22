# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# Standard library imports
import collections
import os
import random
import sys
import tempfile
from string import Template

# Local imports
from . import paths
from .compat import numeric_types, platform, string_types
from .vendor import yaml


KeyValue = collections.namedtuple('KeyValue', 'key value')
Item = collections.namedtuple('Item', 'key value')


class CaseInsensitiveDict(collections.MutableMapping):
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
        if other_cmp is NotImplemented:
            return NotImplemented
        self_cmp = self._comparable_mapping(self)
        return self_cmp == other_cmp

    @classmethod
    def _comparable_mapping(cls, mapping):
        if isinstance(mapping, CaseInsensitiveDict):
            return {item.key.lower(): item.value for item in mapping.values()}
        if isinstance(mapping, collections.Mapping):
            return {key.lower(): value for key, value in mapping.items()}
        return NotImplemented


class EnvironmentDict(CaseInsensitiveDict):
    '''A dict suited to manipulating environment variables.

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
        self._add_condition = kwargs.pop('add_condition', IgnoreCase)
        super(EnvironmentDict, self).__init__(*args, **kwargs)

    def _ensure_list(self, value):
        if value is None:
            return []
        if isinstance(value, env_value_types):
            return [value]
        if isinstance(value, collections.Sequence):
            return list(value)
        raise ValueError('%s could not be converted to a list.' % value)

    def _coerce_value(self, value):
        if isinstance(value, env_value_types):
            return str(value)
        elif isinstance(value, collections.Sequence):
            result = []
            for v in value:
                if v in (None, ''):
                    continue
                result.append(str(value))
            return result
        else:
            raise ValueError(self._value_error % type(value))

    def _default_add_condition(self, current_value, value):
        return value not in current_value

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

        result = self._ensure_list(self.get(key, []))
        if isinstance(value, env_value_types):
            if self._remove_condition(result, value):
                result.remove(value)
        elif isinstance(value, collections.Sequence):
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

        result = self._ensure_list(self.get(key, []))
        value = self._coerce_value(value)

        if isinstance(value, env_value_types):
            if self._add_condition(result, value):
                result.insert(0, value)
        elif isinstance(value, collections.Sequence):
            for v in value:
                if self._add_condition(result, v):
                    result.insert(0, v)

        self[key] = result

    def append(self, key, value, add_check=None):
        '''Append a value to a key.

        Sets the value if the key does not exist.
        '''

        result = self._ensure_list(self.get(key, []))
        value = self._coerce_value(value)

        if isinstance(value, env_value_types):
            if self._add_condition(result, value):
                result.append(value)
        elif isinstance(value, collections.Sequence):
            for v in value:
                if self._add_condition(result, v):
                    result.append(v)

        self[key] = result
    '''

    if platform in v:
        d[k] = v[platform]


def _join_str(d, k, v):
    '''Add a string value to env dict'''

    d[k] = str(v)


def _join_seq(d, k, v):
    '''Add a sequence value to env dict'''

    if k not in d:
        d[k] = list(v)
    elif isinstance(d[k], list):
        for item in reversed(v):
            if item not in d[k]:
                d[k].insert(0, item)
    elif isinstance(d[k], string_types):
        d[k] = list(v) + [d[k]]
    else:
        raise ValueError('Failed to join dict values %s and %s' % (d[k], v))


JOINERS = {
    dict: _join_dict,
    list: _join_seq,
    set: _join_seq,
    tuple: _join_seq,
}

JOINERS.update(
    dict((typ, _join_str) for typ in numeric_types + string_types)
)


def join_dicts(*dicts):
    '''Join a bunch of dicts.

    - Expects keys to be strings
    - Ignores key case
    - Converts numeric and string types to string using str
    - String values overwrite existing keys
    - List values are prepended to existing keys
    '''

    out_dict = CaseInsensitiveDict()

    for d in dicts:

        for k, v in d.items():

            if type(v) not in JOINERS:
                raise KeyError('Invalid type in dict: {}'.format(type(v)))

            JOINERS[type(v)](out_dict, k, v)

    return dict(out_dict)


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
