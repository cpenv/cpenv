============
Modules
============
# TODO

Configuration
=============
The modules configuration is stored in module.yml file within the root directory of the module. For example ``~/.cpenv/myenv/modules/mymodule/module.yml``.

Variables
---------
You can reference environment variables in configuration files by using ``$ENVVAR`` or ``${ENVVAR}``. Additionally cpenv provides the following variables for you to use.

+---------------+----------------------------+
| Variable      | Value                      |
+===============+============================+
| ENVIRON       | Path to parent environment |
+---------------+----------------------------+
| MODULE        | Path to this module        |
+---------------+----------------------------+
| PLATFORM      | win, linux or osx          |
+---------------+----------------------------+
| PYVER         | version of python          |
+---------------+----------------------------+

Sections
--------
Configuration is broken down into the following sections.

environment
+++++++++++
# TODO

dependencies
++++++++++++
# TODO