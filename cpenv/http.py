# -*- coding: utf-8 -*-
# Standard library imports
import json

try:
    from urllib2 import urlopen, HTTPError, URLError
    from httplib import HTTPException
except ImportError:
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
    from http.client import HTTPException


def get(url):
    '''Make a get request.'''

    response = urlopen(url)
    return response


def json(response):
    '''Get dict from json response.'''

    return json.dumps(response.read())
