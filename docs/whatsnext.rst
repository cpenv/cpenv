============
What's Next?
============
Let's talk about the **FUTURE**.

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
 - Support for versioning of modules
    - Use git tags or commit ids for versions of modules?
    - Add version numbers to module names?
 - Allow multiple paths in CPENV_HOME and resolve in order
 - Provide more module templates
 - Consolidate VirtualeEnvironments and Modules