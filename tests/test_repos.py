# -*- coding: utf-8 -*-

# Standard library imports
import os

# Local imports
import cpenv

from . import data_path


def setup_module():
    cpenv.create(
        where=data_path("modules", "testmod-0.1.0"),
        name="testmod",
        version="0.1.0",
        description="A test module",
    )
    cpenv.create(
        where=data_path("modules", "testmod-0.2.0"),
        name="testmod",
        version="0.2.0",
        description="A test module",
    )
    cpenv.create(
        where=data_path("modules", "plugin-0.2.0"),
        name="plugin",
        version="0.2.0",
        description="A test module",
    )
    cpenv.create(
        where=data_path("modules", "fresh/0.1.0"),
        name="fresh",
        version="0.1.0",
        description="A test module",
    )
    cpenv.create(
        where=data_path("modules", "fresh/0.2.0"),
        name="fresh",
        version="0.2.0",
        description="A test module",
    )


def test_LocalRepo_init():
    """Initialize a LocalRepo"""

    cpenv.LocalRepo("test_modules", data_path("modules"))


def test_LocalRepo_list():
    """List modules in a LocalRepo"""

    local_repo = cpenv.LocalRepo("test_modules", data_path("modules"))
    module_specs = local_repo.list()
    expected_names = set(
        [
            "testmod-0.1.0",
            "testmod-0.2.0",
            "plugin-0.2.0",
            "fresh-0.1.0",
            "fresh-0.2.0",
        ]
    )
    resolved_names = set([spec.qual_name for spec in module_specs])
    assert expected_names == resolved_names


def test_LocalRepo_find():
    """Find modules in a LocalRepo"""

    local_repo = cpenv.LocalRepo("test_modules", data_path("modules"))
    tests = [
        ("testmod", ("testmod", "0.2.0")),
        ("testmod-0.1.0", ("testmod", "0.1.0")),
        ("plugin", ("plugin", "0.2.0")),
    ]

    for requirement, result in tests:
        matches = local_repo.find(requirement)
        assert matches[0].name == result[0]
        assert matches[0].version.string == result[1]


def test_LocalRepo_download():
    """Download from a LocalRepo"""

    local_repo = cpenv.LocalRepo("test_modules", data_path("modules"))
    download_path = data_path("downloads", "testmod")

    spec = local_repo.find("testmod-0.2.0")[0]
    module = local_repo.download(spec, download_path)

    assert module.name == "testmod"
    assert module.version.string == "0.2.0"
    assert module.path == download_path


def test_LocalRepo_upload():
    """Upload to a LocalRepo"""

    # Create module to upload
    module = cpenv.create(
        where=data_path("uploads", "upload_module"),
        name="upload_module",
        version="2090.1.0",
        description="A test module",
    )

    # Upload module and check spec
    local_repo = cpenv.LocalRepo("test_modules", data_path("modules"), nested=True)
    spec = local_repo.upload(module)

    assert spec.path == data_path("modules", "upload_module", "2090.1.0")
    assert spec.name == "upload_module"
    assert spec.version.string == "2090.1.0"
    assert os.path.isdir(data_path("modules", "upload_module", "2090.1.0"))


def test_LocalRepo_get_data():
    """Get module data from LocalRepo"""

    # Create module to upload
    local_repo = cpenv.LocalRepo("test_modules", data_path("modules"))
    spec = local_repo.find("testmod-0.2.0")[0]

    data = local_repo.get_data(spec)

    assert data["name"] == "testmod"
    assert data["version"] == "0.2.0"
    assert data["description"] == "A test module"


def test_localize_from_RemoteRepo_to_LocalRepo():
    """Localize a module from a RemoteRepo to a LocalRepo"""

    # Create a module in a RemoteRepo
    cpenv.create(
        where=data_path("remote", "modules", "remote_module-0.1.0"),
        name="remote_module",
        version="0.1.0",
        description="A remote module...",
    )
    remote_repo = cpenv.RemoteRepo("remote_repo", data_path("remote", "modules"))
    remote_spec = remote_repo.find("remote_module-0.1.0")[0]

    # Localize module to a LocalRepo
    local_repo = cpenv.LocalRepo("local_repo", data_path("local", "modules"))
    local_spec = cpenv.Localizer(local_repo).localize([remote_spec])[0]

    assert local_spec.name == "remote_module"
    assert local_spec.path == data_path("local", "modules", "remote_module-0.1.0")
    assert local_spec.version.string == "0.1.0"
    assert os.path.isdir(data_path("local", "modules", "remote_module-0.1.0"))
