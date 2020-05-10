# -*- coding: utf-8 -*-

# Standard library imports
import re
from collections import namedtuple
from functools import total_ordering


__all__ = [
    'ParseError',
    'Version',
    'parse_version',
    'default_version',
]


# Strange nuke version pattern
nuke_version_pattern = (
    r'(?P<major>\d+)'
    r'\.(?P<minor>\d+)'
    r'(?:v)'
    r'(?P<patch>\d+)$'
)
# Modified regex from semver.org
semver_version_pattern = (
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

    def __str__(self):
        return self.string

    def __hash__(self):
        return super(Version, self).__hash__()

    def _comparable(self):
        '''Generate a comparison key for a Version object.

        We use 'zzzzzzzz' as a default in lieu of complicated conditional logic
        to force releases to take precendence over prereleases.
        '''
        return (
            self.major,
            self.minor,
            self.patch,
            self.prerelease or 'zzzzzzzz',
            self.buildmetadata or 'zzzzzzzz',
        )

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Can only compare two Version objects.')

        return self._comparable() < other._comparable()

    def __eq__(self, other):
        if not isinstance(other, Version):
            raise ValueError('Can only compare two Version objects.')

        return self._comparable() == other._comparable()


class ParseError(Exception):
    '''Raised when a parse method fails.'''


def parse_version(string):
    '''Parse and return a Version from the provided string.

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
    # Parse weird nuke versioning
    match = re.search(nuke_version_pattern, string)
    if match:
        return Version(
            major=int(match.group('major')),
            minor=int(match.group('minor')),
            patch=int(match.group('patch')),
            prerelease=None,
            buildmetadata=None,
            string=match.group(0)
        )

    # Parse Semver / Calver
    match = re.search(semver_version_pattern, string)
    if match:
        return Version(
            major=int(match.group('major')),
            minor=int(match.group('minor')),
            patch=int(match.group('patch')),
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
            kwargs[part_name] = int(part)
        return Version(**kwargs)

    raise ParseError('Could not parse version from %s' % string)


def default_version():
    return Version(
        major=0,
        minor=1,
        patch=0,
        prerelease=None,
        buildmetadata=None,
        string='0.1.0',
    )
