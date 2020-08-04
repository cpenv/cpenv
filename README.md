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
Cpenv is a cli tool and python library that allows you to create, edit, publish, and activate Modules.

## Modules
A Module is a folder containing a dependency like Arnold for Maya and a module.yml file that configures it. 
Modules can be as simple or as complex as needed. 

### Create a Module
Use `cpenv create <module>` to use a guide to create a new Module. 
This will create a new folder in your current working directory with a module file in it.
 
### Module file
Each module contains a module.yml file, refered to as a module file. The module file contains
metadata like the name and version of a module, as well as configuration, like environment variables.
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

#### Environment key
Setting a value will create or overwrite it's existing value.
```
SOME_VAR: 'SOME_VALUE'
```

Use the $MODULE variable for module relative paths.
```
RELATIVE_VAR: $MODULE/bin
```

Use lists to prepend values to an environment variable.
```
PATH:
    - $MODULE/bin
```

Use win, linux and osx keys to declar platform specific values. If you leave out a platform, the variable will not be included on that specific platform.
```
PLATFORM_VAR:
    win: 'C:/some/path'
    linux: '/some/path'
    osx: '/some/path'
```

You can also use win, linux and osx keys when prepending values to a variable.
```
PATH:
    - win: $MODULE/squares
      linux: $MODULE/penguin
      osx: $MODULE/macattack
```

Declare and use environment variables to simplify things.
```
BASE: $MODULE/$PLATFORM/base
PATH:
    - $BASE/bin
PYTHONPATH:
    - $BASE/python
```

#### Requires key
The requires key is a list of dependencies that a module needs to function. Currently this is only used for reference, these modules will not be activated automatically.

### Test a Module
When you're working on a module navigate into it's root directory. Then you can activate it using `cpenv activate .`. This is
the best way to validate your module prior to publishing.

### Publish a Module
Once you're Module is ready for production, use `cpenv publish .` to publish it. Publishing a Module uploads it to a Repo
of your choosing. 

## Repos
Repos are storage locations for Modules that support finding, listing, uploading, and downloading Modules via *requirements* like 
`my_module-0.1.0`. Cpenv is configured with the following LocalRepos by default:

- **cwd** - Your current working directory
- **user** - A user specific repo
- **home** - A machine wide repo

Use `cpenv repo list` to display your configured Repos. LocalRepos point directly to folders on your local file system.
Customize the home Repo by setting the `CPENV_HOME` environment variable.

When you activate a module using a requirement, all configured Repos are searched and the best match is used. If the resolved
module is not in a LocalRepo it will be downloaded to your home Repo then activated. This is one of the key features of cpenv 
and allows for strong distributed workflows. For example, you can configure a remote repo like the GithubRepo to store modules 
in a Github organization or you can configure a ShotgunRepo and store your modules directly in a 
[Shotgun studio](https://www.shotgunsoftware.com/) database. [Visit the tk-cpenv repository for more info on using cpenv with Shotgun](https://github.com/cpenv/tk-cpenv)

## Requirements
Requirements are strings used to resolve and activate modules in Repos. They can be versionless like `my_module` or require a 
version like `my_module-0.1.0`. Cpenv supports semver/calver, simple versions (v1), and what I like to call *weird* versions 
like 12.0v2 (The Foundry products). In the future cpenv may support more complex requirements by utilizing 
[resolvelib](https://github.com/sarugaku/resolvelib).
