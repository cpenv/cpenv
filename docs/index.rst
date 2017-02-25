cpenv
=====
Cross-platform Python environment management.

cpenv makes it easy to manage dependencies, environment variables, and applications through the use
of python virtualenvs and modules. Configurations can be shared between windows, linux, or mac and 
deployed directly from git.

How it looks
============

From a terminal:
::
    > cpenv create my_env
    Creating new environment my_env
    ...
    Activating my_env

    [my_env]> cpenv create --module my_module https://github.com/cpenv/template_module.git
    Installing https://github.com/cpenv/template_module.git
    ...

From python:

.. code-block:: python

    import cpenv
    my_env = cpenv.create('my_env)
    my_env.add_module('my_module', 'https://github.com/cpenv/template_module.git')
    my_env.activate()

From an environment config:
::

    environment:
        PATH:
            - '$ENVIRON/relative/path'
    dependencies:
        modules:
            - name: template_module
            repo: https://github.com/cpenv/template_module.git
            branch: master
        pip:
            - requests
        git: []

Installation
============
cpenv is available on pypi: 
::

    pip install cpenv

Make sure you've got `Git <https://git-scm.com>`_ installed and accessible from your command prompt/terminal and you're ready to go. Set $CPENV_HOME where you'd like environments to be created (defaults to ~/.cpenv).


Documentation Contents
======================

.. toctree::
   :maxdepth: 2

   guide
   environments
   modules
   hooks

API Documentation
=================

.. toctree::
   :maxdepth: 2

   api-guide
   api
