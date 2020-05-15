# -*- coding: utf-8 -*-
# Standard library imports
import base64
import io
import os
import re
import warnings
import zipfile

# Local imports
from .. import http, paths
from ..module import Module, ModuleSpec, parse_module_requirement
from ..reporter import get_reporter
from ..vendor import yaml
from ..versions import parse_version, default_version
from .base import Repo


class GithubRepo(Repo):
    '''Supports using Github as a source of modules. If an owner/organization
    is provided, GithubRepo will treat every repo in the organization as
    a Module if the repo has a module.yml file.

    A GithubRepo without an owner/organization is added to cpenv at import.
    This allows cpenv to localize, copy, and clone from requirements matching
    this pattern:

        https://github.com/<owner>/<repo>[@<tag>]

    If a tag is not provided, the latest tag will be used.


    Arguments:
        name (str): Name of this Repo
        owner (str): Github owner or Organization for module lookup (optional)

    Examples:
        # Only supports explicit url requirements
        >>> bare_repo = GithubRepo('github')
        >>> bare_repo.find('https://github.com/some_org/some_module@0.1.0')

        # Supports lookups using standard requirements
        >>> org_repo = GithubRepo('github', owner='some_org')
        >>> org_repo.find('some_module-0.1.0')

        # Also supports listing modules by looking at the repos in the org
        >>> org_repo.list()
    '''

    type_name = 'github'
    _regexes = [
        re.compile(  # Site lookup
            r'https://github\.com/'
            r'(?P<owner>[\w_-]+)/'  # Owner / Organization
            r'(?P<repo>[\w_-]+)(?:\.git)?'  # Repo name
            r'(?:@(?P<version>.*))?'  # Optional tag
        ),
        re.compile(  # ModuleSpec.path lookup
            r'https://api.github\.com/repos/'
            r'(?P<owner>[\w_-]+)/'  # Owner / Organization
            r'(?P<repo>[\w_-]+)'  # Repo name
            r'/zipball'
            r'(?:/(?P<version>.*))?'  # Optional tag
        ),
    ]
    _github_uri = 'https://github.com/'
    _api_uri = 'https://api.github.com/'
    _uris = {
        'owner': _github_uri + '{owner}',
        'tags': _api_uri + 'repos/{owner}/{repo}/tags',
        'repos': _api_uri + 'orgs/{owner}/repos',
        'contents': _api_uri + 'repos/{owner}/{repo}/contents/{file}',
        'archive': _api_uri + 'repos/{owner}/{repo}/zipball'
    }

    def __init__(self, name, owner=None):
        super(GithubRepo, self).__init__(name)
        self.owner = owner
        if owner:
            self.path = self._uris['owner'].format(owner=owner)
        else:
            self.path = self._github_uri

    def _parse_uri(self, uri):
        for regex in self._regexes:
            match = regex.match(uri)
            if match:
                return match.groupdict()

    def _get_tag_specs(self, owner, repo):
        try:
            uri = self._uris['tags'].format(owner=owner, repo=repo)
            response = http.get(uri)
            tags = http.json(response)
            return [tag_to_module_spec(tag, self) for tag in tags]
        except http.HTTPError as e:
            warnings.warn('HTTPError: ' + str(e))
            return []

    def _get_master_spec(self, owner, repo):
        return ModuleSpec(
            name=repo,
            real_name=repo,
            qual_name=repo + '-0.1.0',
            version=default_version(),
            path=self._uris['archive'].format(owner=owner, repo=repo),
            repo=self,
        )

    def _find_url(self, requirement):
        data = self._parse_uri(requirement)
        if not data:
            raise ValueError((
                'Invalid requirement uri: %s\n'
                'Github URI requirements must match: \n'
                '    https://github.com/<owner>/<repo>[@<tag>]'
            ) % requirement)

        if not self._is_repo_module(data['owner'], data['repo']):
            raise ValueError((
                'Github Repository %s '
                'does not contain module.yml file.'
            ) % requirement)

        specs = self._get_tag_specs(data['owner'], data['repo'])
        specs.append(self._get_master_spec(data['owner'], data['repo']))
        return specs

    def _find_req(self, requirement):
        if self.owner is None:
            return []

        name, version = parse_module_requirement(requirement)

        if not self._is_repo_module(self.owner, name):
            return []

        specs = self._get_tag_specs(self.owner, name)
        specs.append(self._get_master_spec(self.owner, name))
        return specs

    def find(self, requirement):
        if requirement.startswith('https://github.com'):
            return self._find_url(requirement)
        else:
            return self._find_req(requirement)

    def _is_repo_module(self, owner, repo):
        # Check if module.yml exists in repo
        file_uri = self._uris['contents'].format(
            file='module.yml',
            owner=owner,
            repo=repo,
        )
        try:
            http.get(file_uri)
            return True
        except http.HTTPError:
            return False

    def list(self):
        if self.owner is None:
            return []

        module_specs = []
        response = http.get(self._uris['repos'].format(owner=self.owner))
        repos = http.json(response)
        for repo in repos:
            owner, repo = repo['full_name'].split('/')
            if not self._is_repo_module(owner, repo):
                continue
            module_specs.extend(self._get_tag_specs(owner, repo))
            module_specs.append(self._get_master_spec(owner, repo))
        return module_specs

    def download(self, module_spec, where, overwrite=False):
        if os.path.isdir(where):
            if overwrite:
                paths.rmtree(where)
            else:
                raise Exception('Module already exists in download location.')

        # Download zipball from github - add a chunk to download_size for zip
        chunk_size = 8192
        download_size = self.get_size(module_spec)
        zip_chunk_size = (download_size / chunk_size) * 10
        progress_bar = get_reporter().progress_bar(
            label='Download %s' % module_spec.name,
            max_size=download_size + zip_chunk_size,
            data={'module_spec': module_spec},
        )
        with progress_bar as progress_bar:
            response = http.get(module_spec.path)
            data = io.BytesIO()
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                progress_bar.update(len(chunk))
                data.write(chunk)

            # Construct and extract in-memory zip archive
            zip_file = zipfile.ZipFile(data)
            zip_file.extractall(where)
            progress_bar.update(zip_chunk_size)

            module = Module(where)
            progress_bar.update(data={
                'module_spec': module_spec,
                'module': module,
            })

        return module

    def upload(self, module, overwrite=False):
        # TODO
        # If the module in question is a git repository
        # we can force a tag at the current commit and push
        # If the module in question is not a git repository - we're out of
        # luck.
        return NotImplemented

    def remove(self, module_spec):
        return NotImplemented

    def get_data(self, module_spec):
        uri_data = self._parse_uri(module_spec.path)
        if not uri_data:
            return {}

        contents_uri = self._uris['contents'].format(
            file='module.yml',
            **uri_data
        )
        response = http.get(contents_uri)
        contents = http.json(response)
        text = base64.b64decode(contents['content'])
        data = yaml.load(text)
        return {
            'name': data.get('name', module_spec.name),
            'version': data.get('version', '0.1.0'),
            'author': data.get('author', ''),
            'email': data.get('email', ''),
            'description': data.get('description', ''),
            'requires': data.get('requires', []),
            'environment': data.get('environment', {}),
        }

    def get_thumbnail(self, module_spec):
        from .. import api
        paths.ensure_path_exists(api.get_cache_path('icons'))

        uri_data = self._parse_uri(module_spec.path)
        if not uri_data:
            return None

        # Cache thumbnail locally
        icon_path = api.get_cache_path(
            'icons',
            module_spec.qual_name + '_icon.png'
        )

        if not os.path.isfile(icon_path):
            contents_uri = self._uris['contents'].format(
                file='icon.png',
                **uri_data
            )
            try:
                response = http.get(contents_uri)
                contents = http.json(response)
                with open(icon_path, 'wb') as f:
                    f.write(contents)
            except http.HTTPError:
                return None

        return icon_path

    def get_size(self, module_spec):
        response = http.get(module_spec.path)
        return response.info()['Content-Length']


def tag_to_module_spec(tag, repo):
    '''Convert github tag data to a ModuleSpec.'''

    name = tag['commit']['url'].split('/')[-3]
    path = tag['zipball_url']
    version = parse_version(tag['name'])
    qual_name = name + '-' + version.string

    return ModuleSpec(
        name=name,
        real_name=qual_name,
        qual_name=qual_name,
        version=version,
        path=path,
        repo=repo,
    )
