
import sys

try:
    from . import yaml2 as yaml_
except ImportError:
    from . import yaml3 as yaml_


# Replace this stub with actual yaml module
sys.modules[__name__] = yaml_
