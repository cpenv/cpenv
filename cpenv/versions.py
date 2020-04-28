# -*- coding: utf-8 -*-

# Standard library imports
import re
from collections import namedtuple
from functools import total_ordering


__all__ = [
    'ParseError',
    'Version',
    'parse',
]


semcal_version_pattern = (
    r'(?:v)?'
    r'(?P<major>\d+)'
    r'\.(?P<minor>\d+)'
    r'\.(?P<patch>\d+)'
    r'(?:-(?P<prerelease>(?:\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
    r'(?:\.(?:\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)
simple_version_pattern = r'(?:v)?(?P<version>(\d+\.?)+)$'
VersionBase = namedtuple(
    'Version',
    ['major', 'minor', 'patch', 'prerelease', 'buildmetadata', 'string']
)


@total_ordering
class Version(VersionBase):

    _defaults = {
        'major': 0,
        'minor': 0,
        'patch': 0,
        'prerelease': None,
        'buildmetadata': None
    }

    def _cmp(self):
        return (
            int(self.major),
            int(self.minor),
            int(self.patch),
            self.prerelease or 'zzzzzzzz',
            self.buildmetadata or 'zzzzzzzz',
        )

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Can only compare two Version objects.')

        return self._cmp() < other._cmp()

    def __eq__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Can only compare two Version objects.')

        return self._cmp() == other._cmp()


class ParseError(Exception):
    '''Raised when a parse method fails.'''


def parse(string):
    '''Attempt to parse a version from the provided string.

    Supports:
      - semver / calver
      - simple versions like: 10, v2, 1.0, 2.2.4

    Arguments:
        string (str): String to parse version from.

    Returns:
        Version object

    Raises:
        ParseError when a version can not be parsed.
    '''

    # Parse Semver / Calver
    match = re.search(semcal_version_pattern, string)
    if match:
        return Version(
            major=match.group('major'),
            minor=match.group('minor'),
            patch=match.group('patch'),
            prerelease=match.group('prerelease'),
            buildmetadata=match.group('buildmetadata'),
            string=match.group(0),
        )

    # Parse Simple version
    match = re.search(simple_version_pattern, string)
    if match:
        kwargs = dict(Version._defaults)
        kwargs['string'] = match.group(0)
        version_parts = match.group('version').split('.')
        for part, part_name in zip(version_parts, ['major', 'minor', 'patch']):
            kwargs[part_name] = part
        return Version(**kwargs)

    raise ParseError('Could not parse version from %s' % string)
