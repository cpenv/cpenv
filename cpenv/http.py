# -*- coding: utf-8 -*-
# Standard library imports
import os
import ssl
from json import dumps as json_dump
from json import loads as json_load

try:
    from urllib2 import urlopen, HTTPError, URLError
    from httplib import HTTPException
except ImportError:
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
    from http.client import HTTPException

try:
    import certifi
except ImportError:
    from .vendor import certifi



def get(url):
    '''Make a get request.'''

    context = ssl.create_default_context(cafile=ca_certs())
    response = urlopen(url, context=context)
    return response


def json(response):
    '''Get dict from json response.'''

    return json_load(response.read().decode())


def ca_certs():
    '''Returns path to vendored certifi/cacert.pem.'''

    package = os.path.dirname(__file__)
    return os.path.join(package, 'vendor', 'certifi', 'cacert.pem')
