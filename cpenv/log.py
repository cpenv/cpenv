'''
Logging Configuration
=====================
'''
import os
import logging
from .utils import unipath

logger = logging.getLogger('cpenv')
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh_formatter = logging.Formatter('%(message)s')
sh.setFormatter(sh_formatter)

fh = logging.FileHandler(unipath('~/cpenv.log'))
fh.setLevel(logging.ERROR)
fh_formatter = logging.Formatter(
    '[%(asctime)s in %(module)s.%(funcName)s @%(lineno)s]\n'
    '%(message)s')
fh.setFormatter(fh_formatter)

logger.addHandler(sh)
logger.addHandler(fh)
