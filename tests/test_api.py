# -*- coding: utf-8 -*-

import os
from nose.tools import assert_raises
import cpenv
from cpenv.utils import rmtree
from . import data_path


def setup_module():
    pass


def teardown_module():
    rmtree(data_path('home'))


def test_create():
    '''Create an environment'''

    cpenv.create('test')
    assert_raises(OSError, cpenv.create, 'test')


def test_add_module():
    '''Add a module'''

    env = cpenv.get_environment('test')
    env.add_module('test_mod', 'https://github.com/cpenv/template_module.git')
    assert_raises(
        OSError,
        env.add_module,
        'test_mod',
        'https://github.com/cpenv/template_module.git'
    )


def test_remove_module():
    '''Remove a module'''

    env = cpenv.get_environment('test')
    mod = env.get_module('test_mod')
    mod.remove()
    assert not os.path.exists(mod.path)


def test_remove_environment():
    '''Remove an environment'''

    env = cpenv.get_environment('test')
    env.remove()
    assert not os.path.exists(env.path)
