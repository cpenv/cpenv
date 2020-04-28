=====
hooks
=====
Hooks are python modules that have a run function. There are many types of hooks each respond to a different event. The run functions first argument is always a VirtualEnvironment instance. Module events are also passed a Module instance.


Available Hooks
===============

- Create
    + pre_create.py
        * signature: run(module, config)
    + post_create.py
        * signature: run(module)
- Activate
    + pre_activate.py
        * signature: run(module)
    + post_activate.py
        * signature: run(module)
- Remove
    + pre_remove.py
        * signature: run(module)
    + post_remove.py
        * signature: run(module)


Global Hooks
============
The global hook path is ``$CPENV_HOME/hooks`` or ``~/.cpenv/hooks`` if the ``$CPENV_HOME`` environment variable is undefined. All hooks are available as global hooks.

Module Hooks
============
Module hooks are stored in a modules hooks directory(``~/.cpenv/test_env/modules/test_module/hooks``) and overide environment and global hooks. Only module event hooks are supported. If the module is not inside an environment
the env argument will be None.
