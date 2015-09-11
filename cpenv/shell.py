from . import platform
from .util import binpath
import subprocess


def cmd():
    '''Return a command to launch a subshell...'''

    if platform == 'win':
        return ['cmd.exe', '/K']
    return ['bash', '--rcfile', binpath('subshell.sh')]


def launch():
    '''Launch a subshell'''

    subprocess.call(cmd())
