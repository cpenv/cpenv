cpenv
======
Cross-platform Python environment management.


Installation
============
 
::

    pip install cpenv

Also make sure you've got `Git <https://git-scm.com>`_ installed and accessible from your command prompt/terminal and you're ready to start using cpenv.

Environment Variables
=====================

- $CPENV_HOME - Path where environments will be created (default: ~/.cpenv)
- $CPENV_ACTIVE - Path to active environment
- $CPENV_APP - Path to active app module


Create
------
::

    cpenv create test

Create an environment named test.


Activate
--------

::

    cpenv activate test

All activated environments are stored in a cache in ~/.cpenv/envcache.yml. First environments are looked up by name in CPENV_HOME path, then looked up in envcache.yml. This means you can store and activate environments by name regardless of where they are stored on the file system, so long as you activate them once by full path. The paths stored in the cache are validated each time you run cpenv.


Deactivate
----------

Each environment runs in a subshell so deactivation is handled through the shell command **exit**.


Modules
=======

Modules are sub environments used to configure DCC applications like Autodesk Maya and The Foundry's Nuke. You can find two examples of Modules at http://github.com/cpenv/maya_module.git and http://github.com/cpenv/nuke_module.git. Each Module includes a module.yml file with a command to launch the application, environment variables, and any python dependencies the Module requires.

Create a Module
---------------

::

    cpenv create --module maya2016 https://github.com/cpenv/maya_module.git

Adds the default maya Module to the active environment test. All Modules are installed to $CPENV_ACTIVE/modules.

Launch a Module
---------------

::

    cpenv launch maya2016

Launches maya2016 Module using the command and arguments provided in the module.yml file. You can also pass additional args.

::

    cpenv launch maya2016 "/path/to/maya_file.mb"

Remove a Module
---------------

::

    cpenv remove --module maya2016


Removing Virtual Environments
=============================

::

    cpenv remove test
