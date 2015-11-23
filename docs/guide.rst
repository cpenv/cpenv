Create and activate an environment
==================================
By default virtual environments will be created in ~/.cpenv. You can override your cpenv home path by setting the CPENV_HOME environment variable.

::

    >>> import cpenv
    >>> myenv = cpenv.create('myenv')
    >>> myenv.activate()


Activate an environment by name or path
=======================================

::

    >>> myenv = cpenv.activate('myenv')

::

    >>> myenv = cpenv.activate('~/.cpenv/myenv')


Application Modules
===================
Application modules are composable sub-environments used to configure specific applications within an environment. Let's add the default module for Autodesk Maya to the previously created environment.

::

    >>> maya2016 = myenv.add_module('maya2016', 'https://github.com/cpenv/maya_module.git')
