# -*- coding: utf-8 -*-

# Third party imports
import pytest

# Local imports
import cpenv
from cpenv import paths

from . import data_path


def setup_module():
    pass


def teardown_module():
    paths.rmtree(data_path("home"))


def test_create():
    """Create a module"""

    # First run creates a module
    cpenv.create(data_path("home", "testmod"), name="testmod", version="0")

    # Second run raises error
    with pytest.raises(OSError):
        cpenv.create(data_path("home", "testmod"), name="testmod", version="0")
