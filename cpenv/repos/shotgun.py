# -*- coding: utf-8 -*-
# Standard library imports
import io
import fnmatch
import os
import warnings
import zipfile

# Local imports
from .. import api, utils
from ..module import Module, ModuleSpec, parse_module_requirement
from ..versions import parse_version
from .base import Repo

try:
    from shotgun_api3 import Shotgun
except ImportError:
    warnings.warn(
        'ShotgunRepo is unavailable.\n'
        'Install the Shotgun API using pip:\n'
        '    pip install git+git://github.com/shotgunsoftware/python-api.git'
    )


class ShotgunRepo(Repo):
    '''Use Shotgun's database as a Repo for modules.

    Requirements:
        A CustomNonProjectEntity named "Module" to be enabled via
        Shotgun site-preferences.

        The following fields must be added to the "Module" entity.
          - archive       File/Link
          - archive_size  Number
          - author        Text
          - description   Text
          - email         Text
          - version       Text

    Arguments:
        name (str): Name of this Repo
        module_entity (str): Name of Module entity (CustomNonProjectEntity01)
        base_url (str): Path to Shotgun site (https://my.shotgunstudio.com)
        script_name (str): Name of Shotgun api script
        api_key (str): Key of Shotgun api script
        api (Shotgun): shotgun_api3.Shotgun instance

    Examples:
        >>> from shotgun_api3 import Shotgun
        >>> sg = Shotgun(base_url, script_name, api_key)
        >>> ShotgunRepo('MyShotgunRepo', api=sg)

        OR

        >>> ShotgunRepo('MyShotgunRepo', base_url, script_name, api_key)
    '''

    type_name = 'shotgun'

    def __init__(
        self,
        name,
        base_url=None,
        script_name=None,
        api_key=None,
        api=None,
        module_entity='CustomNonProjectEntity01',
    ):
        super(ShotgunRepo, self).__init__(name)
        if api:
            # Assume we've received a Shotgun instance
            # This will be done via the tk-cpenv shotgun app
            self._api = api
        else:
            self._api = Shotgun(
                base_url=base_url,
                script_name=script_name,
                api_key=api_key,
            )

        self.base_url = self._api.base_url
        self.path = self._api.base_url
        self.module_entity = module_entity
        self.data_fields = ['code', 'sg_version']

    @property
    def shotgun(self):
        return self._api

    def find(self, requirement):
        name, version = parse_module_requirement(requirement)

        # Build filters
        filters = [['code', 'is', name]]
        exact_filters = list(filters)
        if version:
            exact_filters.append(['sg_version', 'is', version.string])

        # Try exact match first
        entities = self.shotgun.find(
            self.module_entity,
            filters=exact_filters,
            fields=self.data_fields,
        )
        if not entities:
            # Fall back to simple name match
            entities = self.shotgun.find(
                self.module_entity,
                filters=filters,
                fields=self.data_fields,
            )

        module_specs = []
        for entity in entities:
            module_specs.append(entity_to_module_spec(entity, self))

        return api.sort_modules(module_specs, reverse=True)

    def list(self):
        entities = self.shotgun.find(
            self.module_entity,
            filters=[],
            fields=self.data_fields,
        )
        module_specs = []
        for entity in entities:
            module_specs.append(entity_to_module_spec(entity, self))

        return api.sort_modules(module_specs, reverse=True)

    def download(self, module_spec, where, overwrite=False):
        entity = self.shotgun.find_one(
            self.module_entity,
            filters=module_spec_to_filters(module_spec),
            fields=['sg_archive_size', 'sg_archive'],
        )
        archive = entity['sg_archive']

        if not archive:
            print('Module entity has no associated archive.')
            return

        if os.path.isdir(where):
            if overwrite:
                utils.rmtree(where)
            else:
                raise Exception('Module already exists in download location.')

        # Download archive data
        data = self.shotgun.download_attachment(archive)

        # Construct zip_file from in-memory data
        zip_file = zipfile.ZipFile(io.BytesIO(data))

        # Extract to where
        zip_file.extractall(where)
        return Module(where)

    def upload(self, module, overwrite=False):
        entity = self.shotgun.find_one(
            self.module_entity,
            filters=module_spec_to_filters(module),
            fields=['sg_archive_size', 'sg_archive'],
        )
        if entity:
            if overwrite:
                self.shotgun.delete(self.module_entity, entity['id'])
            else:
                raise Exception('Module already uploaded.')

        archive = api.get_cache_path('tmp', module.qual_name + '.zip')
        zip_folder(module.path, archive)
        archive_size = os.path.getsize(archive)

        data = module_to_entity(module, sg_archive_size=archive_size)
        entity = self.shotgun.create(self.module_entity, data)
        self.shotgun.upload(
            self.module_entity,
            entity['id'],
            path=archive,
            field_name='sg_archive',
        )
        return entity_to_module_spec(entity, self)

    def remove(self, module_spec):
        entity = self.shotgun.find_one(
            self.module_entity,
            filters=module_spec_to_filters(module_spec),
            fields=['sg_archive_size', 'sg_archive'],
        )
        if entity:
            self.shotgun.delete(self.module_entity, entity['id'])


def entity_to_module_spec(entity, repo):
    '''Convert entity data to a ModuleSpec.'''

    qual_name = '{code}-{sg_version}'.format(**entity)
    version = parse_version(entity['sg_version'])
    return ModuleSpec(
        name=entity['code'],
        real_name=qual_name,
        qual_name=qual_name,
        version=version,
        path=repo.path,
        repo=repo,
    )


def module_spec_to_filters(module_spec):
    '''Convert a ModuleSpec to a list of filters used in a shotgun query.'''

    return [
        ['code', 'is', module_spec.name],
        ['sg_version', 'is', module_spec.version.string],
    ]


def module_to_entity(module, **fields):
    '''Convert a Module or ModuleSpec to data for an entity in shotgun.'''

    fields.setdefault('code', module.name)
    fields.setdefault('sg_version', module.version.string)
    fields.setdefault('description', getattr(module, 'description', ''))
    fields.setdefault('sg_author', getattr(module, 'author', ''))
    fields.setdefault('sg_email', getattr(module, 'email', ''))
    return fields


def zip_folder(folder, where):
    '''Zip the contents of a folder.'''

    skip = ['__pycache__', '.git', 'thumbs.db', '.venv', 'venv']
    skip_patterns = ['*.pyc']

    parent = os.path.dirname(where)
    if not os.path.isdir(parent):
        os.makedirs(parent)

    # TODO: Count files first so we can report progress of building zip

    with zipfile.ZipFile(where, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, subdirs, files in os.walk(folder):
            rel_root = os.path.relpath(root, folder)

            if root in skip:
                subdirs[:] = []
                continue

            for file in files:
                if any([fnmatch.fnmatch(file, p) for p in skip_patterns]):
                    continue

                zip_file.write(
                    os.path.join(root, file),
                    arcname=os.path.join(rel_root, file)
                )
