environment_config = '''
# Available variables
# $ENVIRON - path to this environment
# $PLATFORM - path to platform
# $PYVER - path to python version

# Wrap variables in brackets when they are nested in valid string Template
# characters. For example:

# DO 'this${variable}isnested/' NOT 'this$variableisnested'

environment: {}
    # RELATIVE_VAR: '$ENVIRON/relative/path'
    # PLATFORM_VAR: '$ENVIRON/$PLATFORM/path'
    # PLATFORM_VARB:
    #    win: 'C:/windows/path'
    #    linux: '/linux/path'
    #    osx: '/mac/path'
dependencies:
    modules: []
        # - name: maya2017
        #   repo: https://github.com/cpenv/maya_module.git
        #   branch: 2017
    git: []
        # - path: '$ENVIRON/path/to/clone'
        #   repo: https://github.com/random/repo.git
        #   branch: master
    pip: []
        # - requests
'''

module_config = '''
# Available variables
# $ENVIRON - path to this modules parent environment
# $MODULE - path to this module
# $PLATFORM - path to platform
# $PYVER - path to python version

# Wrap variables in brackets when they are nested in valid string Template
# characters. For example:

# DO 'this${variable}isnested/' NOT 'this$variableisnested'

environment: {}
    # RELATIVE_VAR: '$ENVIRON/relative/path'
    # PLATFORM_VAR: '$ENVIRON/$PLATFORM/path'
    # PLATFORM_VARB:
    #    win: 'C:/windows/path'
    #    linux: '/linux/path'
    #    osx: '/mac/path'
dependencies:
    modules: []
        # - name: maya2017
        #   repo: https://github.com/cpenv/maya_module.git
        #   branch: 2017
    git: []
        # - path: '$ENVIRON/path/to/clone'
        #   repo: https://github.com/random/repo.git
        #   branch: master
    pip: []
        # - requests
'''