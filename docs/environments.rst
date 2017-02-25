============
Environments
============
# TODO describe what environments are

Environment Variables
=====================

+---------------+-------------------------------+---------- + 
| Variable      | Description                   | Default   | 
+===============+===============================+===========+ 
| CPENV_HOME    | Where to create environment   | ~/.cpenv  | 
+---------------+-------------------------------+-----------+ 
| CPENV_ACTIVE  | Path to active environment    |    Null   |
+---------------+-------------------------------+-----------+ 
| CPENV_MODULES | List of Active modules        |    Null   |
+---------------+-------------------------------+-----------+ 

Configuration
=============
The environment variables configuration is stored in an environment.yml file within the root directory of the environment. For example ``~/.cpenv/myenv/environment.yml``.

Variables
---------
You can reference environment variables in configuration files by using ``$ENVVAR`` or ``${ENVVAR}``. Additionally cpenv provides the following variables for you to use.
+---------------+--------------------------+
| Variable      | Value                    |
+===============+==========================+
| ENVIRON       | Path to this environment |
+---------------+--------------------------+
| PLATFORM      | win, linux or osx        |
+---------------+--------------------------+
| PYVER         | version of python        |
+---------------+--------------------------+

Sections
--------
Configuration is broken down into the following sections.

environment
+++++++++++
Environment section examples

dependencies
++++++++++++
dependencies section examples