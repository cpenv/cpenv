# -*- coding: utf-8 -*-
# Standard library imports
import io
import os
import zipfile
from functools import partial

# Local imports
from .. import http, paths
from ..module import Module, ModuleSpec, parse_module_requirement, sort_modules
from ..reporter import get_reporter
from ..vendor import yaml
from ..vendor.cachetools import TTLCache, cachedmethod, keys
from ..versions import parse_version
from .base import Repo


class S3Repo(Repo):
    '''Use an Amazon S3 Storage Bucket as a Repo for modules.

    Requirements:

        - S3 Storage bucket with ACCESS_KEY and STORAGE_KEY for authentication.
        - boto3: python AWS API.

    Arguments:
        name (str): Name of this Repo
        bucket (str): Name of storage bucket.
        access_key (str): AWS Access Key
        secret_key (str): AWS Secret Key

    Examples:
        >>> S3Repo('My S3 Repo', 'my-s3-repo', <access_key>, <api_key>)
    '''

    type_name = 's3'

    def __init__(
        self,
        name,
        bucket,
        access_key,
        secret_key,
    ):
        super(S3Repo, self).__init__(name)

        import boto3
        self._client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        self.cache = TTLCache(maxsize=10, ttl=60)

    @property
    def client(self):
        return self._client

    def clear_cache(self):
        self.cache.clear()

    @cachedmethod(lambda self: self.cache, key=partial(keys.hashkey, 'find'))
    def find(self, requirement):
        name, version = parse_module_requirement(requirement)

        # TODO Find module by requirement in S3

        module_specs = []
        return sort_modules(module_specs, reverse=True)

    @cachedmethod(lambda self: self.cache, key=partial(keys.hashkey, 'list'))
    def list(self):

        # TODO List all modules in S3

        module_specs = []
        return sort_modules(module_specs, reverse=True)

    def download(self, module_spec, where, overwrite=False):

        # TODO Find module_spec in S3
        obj = None
        if not obj:
            # TODO Show error
            return

        if os.path.isdir(where):
            if overwrite:
                paths.rmtree(where)
            else:
                raise Exception('Module already exists in download location.')

        # TODO Download archive
        module = None
        return module

    def upload(self, module, overwrite=False):

        # TODO Check if module is already uploaded
        obj = None
        if obj:
            if overwrite:
                # TODO Delete existing module
                pass
            else:
                raise Exception('Module already uploaded.')

        # TODO Upload
        root_obj = None
        return obj_to_module_spec(root_obj)

    def remove(self, module_spec):
        # TODO Delete existing module in s3 bucket
        pass

    def get_data(self, module_spec):

        # TODO Read metadata
        metadata = None

        # Load module.yml data from sg_data field
        try:
            data = yaml.safe_load(metadata)
        except Exception as e:
            print('Error: ' + e.message)
            print('Failed to load data from sg_data field.')
            data = {}

        # Fill missing data with entity level data
        data.setdefault('name', module_spec['name'])
        data.setdefault('version', module_spec['version'])
        data.setdefault('author', '')
        data.setdefault('email', '')
        data.setdefault('description', '')
        data.setdefault('requires', [])
        data.setdefault('environment', {})

        return data

    def get_thumbnail(self, module_spec):
        from .. import api

        # TODO Find Thumbnail
        obj = None

        # Ensure icons cache dir exists
        icons_root = api.get_cache_path('icons')
        if not os.path.isdir(icons_root):
            os.makedirs(icons_root)

        # TODO Cache thumbnail locally
        icon_path = api.get_cache_path(
            'icons',
            module_spec.qual_name + '_icon.png'
        )
        if not os.path.isfile(icon_path):
            # TODO Download thumbnail
            try:
                data = ''
                with open(icon_path, 'wb') as f:
                    f.write(data)
            except Exception:
                return

        return icon_path

    def get_size(self, spec):
        '''Query S3 for module size.'''

        return 0


def obj_to_module_spec(s3obj, repo):
    '''Convert s3obj to ModuleSpec.'''

    qual_name = ''
    version = parse_version('')
    url = ''
    return ModuleSpec(
        name='',
        real_name=qual_name,
        qual_name=qual_name,
        version=version,
        path=url,
        repo=repo,
    )


def module_to_metadata(module, **fields):
    '''Convert a Module or ModuleSpec to data for an entity in shotgun.'''

    fields.setdefault('name', module.name)
    fields.setdefault('version', module.version.string)
    fields.setdefault('description', getattr(module, 'description', ''))
    fields.setdefault('author', getattr(module, 'author', ''))
    fields.setdefault('email', getattr(module, 'email', ''))
    data = module.raw_config.strip('\n')
    fields.setdefault('data', data)
    return fields
