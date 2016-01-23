# -*- coding: utf-8 -*-

'''
Logging Configuration
=====================
'''

import logging
import os
from .utils import unipath

logger = logging.getLogger('cpenv')
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh_formatter = logging.Formatter('\n%(message)s')
sh.setFormatter(sh_formatter)

user_cpenv = unipath('~/.cpenv')
if not os.path.exists(user_cpenv):
    os.mkdir(user_cpenv)
fh = logging.FileHandler(unipath(user_cpenv, 'cpenv.log'))
fh.setLevel(logging.ERROR)
fh_formatter = logging.Formatter(
    '[%(asctime)s in %(module)s.%(funcName)s @%(lineno)s]\n'
    '%(message)s')
fh.setFormatter(fh_formatter)

logger.addHandler(sh)
logger.addHandler(fh)
