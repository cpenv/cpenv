<p align="center">
    <img src="https://raw.github.com/cpenv/cpenv/master/res/icon_dark.png"/>
</p>

# cpenv
Manage software plugins, project dependencies and environment
variables using Modules.

<p align="center">
    <img src="https://raw.github.com/cpenv/cpenv/master/res/demo.gif"/>
</p>

# Installation
The recommended method of installing cpenv is via [pipx](https://pipxproject.github.io/pipx).
Pipx is used to install python cli applications in isolation.

```
pipx install cpenv
```
```
pipx upgrade cpenv
```
```
pipx uninstall cpenv
```

# Overview
Cpenv is a cli tool and python library used to create, edit, publish, and activate Modules. A Module is a folder containing a dependency, like Arnold for Maya, and a module file that configures it.

## Environment Variables
| Variable                 | Description                            | Default |
| ------------------------ | -------------------------------------- | ------- |
| CPENV_HOME               | Customize path to cpenv home           |         |
| CPENV_DISABLE_PROMPT     | Disable prompt when modules activated  | 0       |
| CPENV_ACTIVE_MODULES     | List of activated modules              |         |
| CPENV_SHELL              | Preferred subshell like "powershell"   |         |
| CPENV_ENABLE_LOCKFILES   | Enable lockfiles during localization   | 0       |

## Example Modules
- [snack](https://github.com/cpenv/snack)

## Create a Module
Use `cpenv create <module>` to use a guide to create a new Module.
This will create a new folder in your current working directory with a module file in it.

## Edit a Module
Each Module contains a module.yml file, referred to as a module file. A module file contains metadata like the name and version of a module, as well as configuration, like environment variables.
```
# Variables
# $MODULE - path to this module
# $PLATFORM - platform name (win, mac, linux)
# $PYVER - python version (2.7, 3.6...)

# Wrap variables in brackets when they are nested within a string.
#     DO 'this${variable}isnested/' NOT 'this$variableisnested'

name: 'my_module'
version: '0.1.0'
description: 'My first module.'
author: 'Me'
email: 'me@email.com'
requires: []
environment:
    MY_MODULE_VAR: 'Test'
```

### Environment key
Setting a value will insert a key or overwrite it's existing value.
```
SOME_VAR: 'SOME_VALUE'
```

Use the $MODULE variable for module relative paths.
```
RELATIVE_VAR: $MODULE/bin
```

Use lists to prepend values to a key.
```
PATH:
    - $MODULE/bin
```

Use `win`, `linux` and `mac or osx` keys to declare platform specific values. If you leave out a platform, the variable will not be included on that platform.
```
PLATFORM_VAR:
    mac: /mnt/some/path
    linux: /Volumes/some/path
    win: C:/some/path
```

You can also use platform keys when prepending values to a variable.
```
PATH:
    - mac: $MODULE/macattack
      linux: $MODULE/penguin
      win: $MODULE/squares
```

Reuse environment variables to simplify things.
```
BASE: $MODULE/$PLATFORM/base
PATH:
    - $BASE/bin
PYTHONPATH:
    - $BASE/python
```

#### Advanced
The implicit set and prepend operations above cover the most common use cases when modifying environment variables. For more advanced use cases you can use the following explicit operation keys.
```
SVAR:
    set:
        - Value0
        - Value1
PVAR:
    prepend:
        - X
RVAR:
    unset: 1
PATH:
    remove:
        - C:/Python27
        - C:/Python27/Scripts
PYTHONPATH:
    append:
        - $MODULE/python
        - $MODULE/lib
```

You can also uses lists of opreations to perform complex modifications.
```
PATH:
    - remove: /some/file/path
    - append: /some/other/path
    - prepend: /one/more/path
```

One workflow that this enables is the use of modules solely for the purpose of overriding environment variables. Imagine you have a module `my_tool` and it uses a variable `MY_TOOL_PLUGINS` to lookup plugins.
```
name: my_tool
...
environment:
    MY_TOOL_PLUGINS:
        - //studio/dev/my_tool/plugins
        - //studio/projects/test_project/plugins
```

Now imagine you have a new project and you want `my_tool` to look at a different location for plugins just for that project. Rather than create a new version of the `my_tool` module, create a override module. We might name this module after our project, `project_b`.
```
name: project_b
...
environment:
    MY_TOOL_PLUGINS:
        set:
            - //studio/prod/my_tool/plugins
            - //studio/projects/project_b/plugins
```

All we have to do is activate `my_tool` and `project_b` in that order to make sure our overrides are used.
```
> cpenv activate my_tool project_b
```

#### Requires key
The requires key is a list of dependencies that a module needs to function. Currently this is only used for reference, these modules will not be activated automatically.

## Test a Module
When you're working on a module navigate into it's root directory. Then you can activate it using `cpenv activate .`. This is
the best way to validate your module prior to publishing.

## Publish a Module
Once you're Module is ready for production, use `cpenv publish .` to publish it. Publishing a Module uploads it to a Repo of your choosing.

# Repos
Repos are storage locations for Modules that support finding, listing, uploading, and downloading Modules via *requirements* like
`my_module-0.1.0`. Cpenv is configured with the following LocalRepos by default:

- **cwd** - Your current working directory
- **user** - A user specific repo
- **home** - A machine wide repo

Use `cpenv repo list` to display your configured Repos. LocalRepos point directly to folders on your local file system.
Customize the home Repo by setting the `CPENV_HOME` environment variable.

When you activate a module using a requirement, all configured Repos are searched and the best match is used. If the resolved
module is not in a LocalRepo it will be downloaded to your home Repo then activated. This is one of the key features of cpenv
and allows for strong distributed workflows. For example, you can configure a remote repo like the ShotgunRepo and store your modules directly in a
[Shotgun studio](https://www.shotgunsoftware.com/) database. [Visit the tk-cpenv repository for more info on using cpenv with Shotgun](https://github.com/cpenv/tk-cpenv)

# Requirements
Requirements are strings used to resolve and activate modules in Repos. They can be versionless like `my_module` or require a
version like `my_module-0.1.0`. Cpenv supports semver/calver, simple versions (v1), and what I like to call *weird* versions
like 12.0v2 (The Foundry products). In the future cpenv may support more complex requirements by utilizing
[resolvelib](https://github.com/sarugaku/resolvelib).

# Locking
It may be desirable to have interprocess locking around module localization. One use case I've run into is with Deadline rendering on workers with multiple gpus. In that case, a single worker may be rendering multiple frames simultaneously, and therefore, it's possible that the worked may try to download the same module at the same time. To enable interprocess locking via lockfiles, set the environment variable `CPENV_ENABLE_LOCKFILES` to 1.
