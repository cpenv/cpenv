# -*- coding: utf-8 -*-

# Local imports
from cpenv import mappings
from cpenv.compat import platform


def test_platform_values():
    """join_dicts with platform values"""

    tests = {
        "implicit_set": {
            "mac": "mac",
            "linux": "linux",
            "win": "win",
        },
        "implicit_prepend": {
            "mac": ["mac0", "mac1"],
            "linux": ["linux0", "linux1"],
            "win": ["win0", "win1"],
        },
        "explicit_set": {
            "set": {
                "mac": "mac",
                "linux": "linux",
                "win": "win",
            }
        },
        "explicit_ops": {
            "mac": [{"append": "mac0"}, {"prepend": "mac1"}],
            "linux": [{"append": "linux0"}, {"prepend": "linux1"}],
            "win": [{"append": "win0"}, {"prepend": "win1"}],
        },
    }
    expected = {
        "implicit_set": tests["implicit_set"],
        "implicit_prepend": tests["implicit_prepend"],
        "explicit_set": tests["explicit_set"]["set"],
        "explicit_ops": {
            "mac": ["mac1", "mac0"],
            "linux": ["linux1", "linux0"],
            "win": ["win1", "win0"],
        },
    }
    results = mappings.join_dicts(tests)
    p = platform
    assert results["implicit_set"] == expected["implicit_set"][p]
    assert results["implicit_prepend"] == expected["implicit_prepend"][p]
    assert results["explicit_set"] == expected["explicit_set"][p]
    assert results["explicit_ops"] == expected["explicit_ops"][p]


def test_join_case_insensitivity():
    """join_dicts is case insensitive"""

    a = {"Var": "a"}  # Original mixed case
    b = {"VAR": "b"}  # UPPER - set
    c = {"var": ["0", "1"]}  # lower - prepend

    # Ensure Var is properly set and case of key is changed
    result = mappings.join_dicts(a, b)
    assert result["VAR"] == "b"

    # Ensure Var is properly set, prepended to and case of key is changed
    result = mappings.join_dicts(a, b, c)
    assert result["var"] == ["0", "1", "b"]


def test_implicit_set_values():
    """join_dicts implicitly sets values"""

    a = {"var": ["x", "y"]}
    b = {"var": "z"}
    c = {"var": "a"}

    result = mappings.join_dicts(a, b)
    assert result["var"] == b["var"]

    result = mappings.join_dicts(a, b, c)
    assert result["var"] == c["var"]


def test_implicit_prepend_values():
    """join_dicts implicitly prepends values"""

    a = {"var": "z"}
    b = {"var": ["x", "y"]}
    c = {"var": ["0", "1"]}

    result = mappings.join_dicts(a, b)
    assert result["var"] == ["x", "y", "z"]

    result = mappings.join_dicts(a, b, c)
    assert result["var"] == ["0", "1", "x", "y", "z"]


def test_explicit_set():
    """join_dicts with explicitly set items"""

    a = {"A": "0", "B": ["1", "2"]}

    # Explicit set str, list, non-existant key
    b = {
        "A": {"set": "1"},
        "B": {"set": ["2", "3"]},
        "C": {"set": "4"},
    }
    result = mappings.join_dicts(a, b)
    assert result == {"A": "1", "B": ["2", "3"], "C": "4"}

    # Explicit set in list of ops
    c = {
        "A": [
            {"set": "10"},
            {"append": "20"},
        ]
    }
    result = mappings.join_dicts(a, b, c)
    assert result == {"A": ["10", "20"], "B": ["2", "3"], "C": "4"}


def test_explicit_unset():
    """join_dicts with explicitly unset keys"""

    a = {"A": "0"}
    b = {"A": {"unset": "1"}}
    result = mappings.join_dicts(a, b)
    assert result == {}


def test_explicit_append():
    """join_dicts with explicitly appended values"""

    a = {"A": "0"}

    # Append one value
    b = {"A": {"append": "1"}}
    result = mappings.join_dicts(a, b)
    assert result == {"A": ["0", "1"]}

    # Append list of values
    c = {"A": {"append": ["2", "3"]}}
    result = mappings.join_dicts(a, b, c)
    assert result == {"A": ["0", "1", "2", "3"]}

    # Multiple append operations
    d = {"A": [{"append": "4"}, {"append": "5"}]}
    result = mappings.join_dicts(a, b, c, d)
    assert result == {"A": ["0", "1", "2", "3", "4", "5"]}

    # Append to non-existant var
    e = {"B": {"append": "6"}}
    result = mappings.join_dicts(a, b, c, d, e)
    assert result == {"A": ["0", "1", "2", "3", "4", "5"], "B": ["6"]}

    # Append duplicates are ignored
    f = {"A": {"append": ["0", "5", "6"]}}
    result = mappings.join_dicts(a, b, c, d, e, f)
    assert result == {"A": ["0", "1", "2", "3", "4", "5", "6"], "B": ["6"]}


def test_explicit_prepend():
    """join_dicts with explicitly prepended values"""

    a = {"A": "0"}

    # Prepend one value
    b = {"A": {"prepend": "1"}}
    result = mappings.join_dicts(a, b)
    assert result == {"A": ["1", "0"]}

    # Prepend list of values
    c = {"A": {"prepend": ["2", "3"]}}
    result = mappings.join_dicts(a, b, c)
    assert result == {"A": ["2", "3", "1", "0"]}

    # Multiple prepend operations
    d = {"A": [{"prepend": "4"}, {"prepend": "5"}]}
    result = mappings.join_dicts(a, b, c, d)
    assert result == {"A": ["5", "4", "2", "3", "1", "0"]}

    # Prepend to non-existant var
    e = {"B": {"prepend": "6"}}
    result = mappings.join_dicts(a, b, c, d, e)
    assert result == {"A": ["5", "4", "2", "3", "1", "0"], "B": ["6"]}

    # Prepend duplicates are ignored
    f = {"A": {"prepend": ["0", "5", "6"]}}
    result = mappings.join_dicts(a, b, c, d, e, f)
    assert result == {"A": ["6", "5", "4", "2", "3", "1", "0"], "B": ["6"]}


def test_explicit_remove():
    """join_dicts with explicitly removed values"""

    a = {"A": ["0", "1", "2", "3", "4"]}

    # Remove one value
    b = {"A": {"remove": "1"}}
    result = mappings.join_dicts(a, b)
    assert result == {"A": ["0", "2", "3", "4"]}

    # Remove list of values
    c = {"A": {"remove": ["2", "4"]}}
    result = mappings.join_dicts(a, b, c)
    assert result == {"A": ["0", "3"]}

    # Multiple remove operations
    d = {"A": [{"remove": "0"}, {"remove": "3"}], "B": {"remove": "6"}}
    result = mappings.join_dicts(a, b, c, d)
    assert result == {}


def test_explicit_complex_operation():
    """join_dicts with multiple explicit operations"""

    a = {
        "A": ["0", "1", "2"],
        "B": "100",
        "C": ["0"],
        "D": "200",
    }
    b = {
        "A": [
            {"remove": ["1", "2"]},
            {"append": "B"},
            {"prepend": ["A", "C"]},
        ],
        "B": [
            {"set": ["A", "B"]},
            {"prepend": "C"},
            {"remove": "B"},
        ],
        "C": [{"set": ["A", "B", "C"]}, {"prepend": "Z"}],
        "D": {"remove": "200"},
    }
    expected = {
        "A": ["A", "C", "0", "B"],
        "B": ["C", "A"],
        "C": ["Z", "A", "B", "C"],
    }
    result = mappings.join_dicts(a, b)
    assert result == expected


def test_env_to_dict():
    """env_to_dict converts environment mapping to dict"""

    env = {
        "PATH": "X:Y:Z",
        "VAR": "VALUE",
    }
    result = mappings.env_to_dict(env, pathsep=":")
    assert result == {"PATH": ["X", "Y", "Z"], "VAR": "VALUE"}


def test_dict_to_env():
    """dict_to_env converts dict to environment mapping"""

    data = {
        "PATH": ["X", "Y", "Z"],
        "VAR": "VALUE",
    }
    result = mappings.dict_to_env(data, pathsep=":")
    assert result == {"PATH": "X:Y:Z", "VAR": "VALUE"}
