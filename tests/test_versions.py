# -*- coding: utf-8 -*-

# Third party imports
from nose.tools import assert_raises

# Local imports
from cpenv.versions import ParseError, parse_version


def test_parse_version():
    '''Parse semver, calver, and simple version strings'''

    # These should be parsed by parsers.semver_version_pattern
    basic_semver = [
        parse_version('0.1.0'),
        parse_version('v0.1.0'),
        parse_version('module0.1.0'),
        parse_version('module-0.1.0'),
        parse_version('module_0.1.0'),
        parse_version('modulev0.1.0'),
        parse_version('module-v0.1.0'),
        parse_version('module_v0.1.0'),
        parse_version('module2-0.1.0'),
    ]
    for version in basic_semver:
        assert version.major == 0
        assert version.minor == 1
        assert version.patch == 0
        assert not version.prerelease
        assert not version.buildmetadata

    full_semver_spec = [
        parse_version('10.2.19-dev+02ab'),
        parse_version('v10.2.19-dev+02ab'),
        parse_version('module10.2.19-dev+02ab'),
        parse_version('module-10.2.19-dev+02ab'),
        parse_version('module_10.2.19-dev+02ab'),
        parse_version('modulev10.2.19-dev+02ab'),
        parse_version('module-v10.2.19-dev+02ab'),
        parse_version('module_v10.2.19-dev+02ab'),
        parse_version('module1-10.2.19-dev+02ab'),
    ]

    for version in full_semver_spec:
        assert version.major == 10
        assert version.minor == 2
        assert version.patch == 19
        assert version.prerelease == 'dev'
        assert version.buildmetadata == '02ab'

    largever_spec = [
        parse_version('10.1.0.234'),
        parse_version('v10.1.0.234'),
        parse_version('module10.1.0.234'),
        parse_version('module_10.1.0.234'),
        parse_version('module-10.1.0.234'),
        parse_version('module-v10.1.0.234'),
    ]
    for version in largever_spec:
        assert version.major == 10
        assert version.minor == 1
        assert version.patch == 0
        assert version.buildmetadata == 234
        assert not version.prerelease

    # These should be parsed by versions.simple_version_pattern
    version = parse_version('module1')
    assert version.string == '1'
    assert version.major == 1
    assert not version.minor
    assert not version.patch

    version = parse_version('module-1')
    assert version.string == '1'
    assert version.major == 1
    assert not version.minor
    assert not version.patch

    version = parse_version('module-v20')
    assert version.string == 'v20'
    assert version.major == 20
    assert not version.minor
    assert not version.patch

    version = parse_version('modulev1.0')
    assert version.string == 'v1.0'
    assert version.major == 1
    assert version.minor == 0
    assert not version.patch


def test_parse_version_raises():
    '''Parse version raises ParseError when parse fails'''

    bad_strings = [
        'mod10funk',
        'no-v',
        '10-0_module',
        'module',
    ]

    for string in bad_strings:
        assert_raises(ParseError, parse_version, string)


def test_compare_versions():
    '''Validate Version comparisons'''

    version_strings = [
        '10.1.5-alpha',
        '10.1.5',
        '3.2',
        '0.1.1',
        '10.20.5',
        '2.0',
        '0.1.0',
        '3.1.9',
    ]
    expected_order = [
        '0.1.0',
        '0.1.1',
        '2.0',
        '3.1.9',
        '3.2',
        '10.1.5-alpha',
        '10.1.5',
        '10.20.5',
    ]

    # Parse and sort
    version_objects = [parse_version(v) for v in version_strings]
    ordered_versions = [v.string for v in sorted(version_objects)]
    assert ordered_versions == expected_order
