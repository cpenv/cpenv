# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
import pytest

# Local imports
import cpenv
from cpenv import paths

from . import data_path


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():

    # Setup
    cpenv.set_home_path(data_path("home"))

    yield

    # Teardown
    paths.rmtree(data_path())
