# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

available = True
try:
    # If you pip installed cpenv requests will be available
    import requests
except ImportError:
    # Otherwise, there is a strong chance that pip is installed
    from pip._vendor import requests
except ImportError:
    available = False

# Replace this stub with the actual requests package
if available:
    requests.available = True
    sys.modules[__name__] = requests
else:
    raise ImportError("No module named 'requests'")
