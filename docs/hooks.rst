=====
hooks
=====
Hooks are python modules that have a run function. There are many types of hooks each respond to a different event. The run functions first argument is always a VirtualEnvironment instance. Module events are also passed a Module instance.


Available Hooks
===============

- Activate
    + preactivate.py
        * signature: run(env)
    + postactivate.py
        * signature: run(env)
- Create
    + precreate.py
        * signature: run(env)
    + postcreate.py
        * signature: run(env)
- Remove
    + preremove.py
        * signature: run(env)
    + postremove.py
        * signature: run(env)


Global Hooks
============
The global hook path is ``$CPENV_HOME/hooks`` or ``~/.cpenv/hooks`` if the ``$CPENV_HOME`` environment variable is undefined. All hooks are available as global hooks.

Module Hooks
============
Module hooks are stored in a modules hooks directory(``~/.cpenv/test_env/modules/test_module/hooks``) and overide environment and global hooks. Only module event hooks are supported. If the module is not inside an environment
the env argument will be None.
