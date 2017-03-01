============
What's Next?
============

Changes and Features
====================

 - Automatically track environment config dependencies
    - wrap pip to add/remove dependencies
 - Give modules their own cli multi-command
    - ``cpenv module add``
    - ``cpenv module remove``
 - Shared modules 
    - store in $CPENV_HOME/modules
    - resolver to look 'em up
 - Allow multiple paths in CPENV_HOME and resolve in order
 - Allow modules to provide commands other than launch
    - Like entry-points from setuptools?
    - As sub-commands of the cpenv cli?
 - Support for versioning of modules
    - Use git tags or commit ids for versions of modules?
    - Add version numbers to module names?
 - Add a build section to module configs
    - Provide a list of commands to run
    - Subsection for build environment
 - Add a test section to module configs
    - Provide a list of commands to run
    - Sub-section build environment
 - Provide more module templates
 - Consolidate VirtualeEnvironments and Modules
