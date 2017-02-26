=====
Guide
=====
This section will guide you through the process of creating an environment suitable for a small vfx production. The environment will include modules for Autodesk's Maya, The Foundry's Nuke, and Google's Zync. If you want to fully follow along, you'll need Maya 2017, Nuke 10.5v2, and Zync installed. Launch your terminal and let's get started.

Create an environment
=====================
The default location for cpenv environments is ``~/.cpenv``. You can change the location where environments are created and looked up by setting the environment variable **CPENV_HOME**. In practice it's common to set **CPENV_HOME** to a network share, that way everyone has access to the same environments.

::

    > cpenv create vfx_env

    Creating new environment vfx_env
    ...
    Activating vfx_env

    [vfx_env]> 

The new prompt is prefixed by ``[vfx_env]``, this let's us known which environment is active. You can access the path to the currently active environment through the environment variable **CPENV_ACTIVE**, in this case ``~/.cpenv/vfx_env``.

.. note:: cpenv environments are standard python virtualenvs with hooks and a configuration file to allow customization.

Add modules from Git
====================
Let's create modules in vfx_env for Maya, Nuke, and Zync. We'll create the modules from git repos.
::

    > cpenv create --module maya2017 https://github.com/cpenv/maya_module.git
    Installing https://github.com/cpenv/maya_module.git
    ...

    > cpenv create --module nuke10.5 https://github.com/cpenv/nuke_module.git
    Installing https://github.com/cpenv/nuke_module.git
    ...

Now we have two modules installed maya2017 and nuke10.5. Essentially all we've done is cloned these two repos into the vfx_env's modules folder ``$CPENV_ACTIVE/modules``. You can make changes to these modules by modifying their module.yml configuration files and adding scripts or plugins to the appropriate folders within the modules. 

.. tip:: Launch your text editor using $CPENV_ACTIVE to make modifications to your env and modules. I use sublime text: ``subl $CPENV_ACTIVE`` on linux and mac or ``subl %CPENV_ACTIVE%`` on windows.

Both of these modules have a command configured to launch Maya and Nuke respectively. Launch Maya like this:

::

    > cpenv launch maya2017

    Launching maya2017

In your Maya command output window on Windows, or in your terminal on Linux you should see the following message:

::

    =======================================
    Running userSetup.py in maya2017 module
    =======================================

A module with a hook
====================
The Zync module is a little more complex. It makes use of the postcreate hook to configure Zync by prompting
the user for their zync.io URL.

::

    > cpenv create --module zync https://github.com/cpenv/zync_module.git
    Installing https://github.com/cpenv/zync_module.git
    ...
    ZYNC: Validating config
    Enter your zync url...[https://YOUR_PREFIX.zync.io] https://vfxstudio.zync.io
    ZYNC: Testing  https://vfxstudio.zync.io
    ZYNC: URL does not seem to exist...
    Use it anyway? [Y/n] Y
    ZYNC: Updating module config with user values
    ZYNC: Configuring zync using these values...
        ZYNC_URL:  https://vfxstudio.zync.io
        API_DIR:  C:\Users\danie\.cpenv\vfx_env\modules\zync/zync-python
    ZYNC: Writing zync-maya/config_maya.py
    ZYNC: Writing zync-nuke/config_nuke.py
    ZYNC: Writing zync-python/config.py

In this case I'm using a dummy URL ``https://vfxstudio.zync.io`` so we're prompted to ``Use it anyway?``. If you have a zync account input your studios URL instead. Now we can activate the zync module in order to have access to zync from Maya.

::

    [vfx_env]> cpenv activate zync

    Activating zync

    [vfx_env:zync]> cpenv launch maya2017

    Launching maya2017

You should now have a Zync shelf available within Maya 2017.

Activating environments
=======================
Now that we've created our vfx_env, let's look at activating it from scratch. First we'll use ``exit`` to deactivate the vfx_env environment and zync module:

::

    [vfx_env:zync]> exit
    [vfx_env]> exit
    >

Notice the quirk here, we've got to ``exit`` twice, because we activated the zync environment when we were already in a subshell for vfx_env. Let's activate both the vfx_env and the zync module simultaneously.

::

    > cpenv activate vfx_env zync
    [vfx_env:zync]>

Simple, all we need to do is supply a list of an environment and any number of modules and cpenv will resolve them appropriately. Since we activated both vfx_env and zync at the same time, when we ``exit`` now we'll pop right out of the subshell to the original shell.

::

   [vfx_env:zync]> exit
   >

Now you probably want to customize your setup. Head on over to the :doc:`environments` or :doc:`modules` pages to learn more.
