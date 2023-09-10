# Local imports
from .base import Repo
from .filesystem import LocalRepo, RemoteRepo
from .shotgun import ShotgunRepo

registry = {
    LocalRepo.type_name: LocalRepo,
    RemoteRepo.type_name: RemoteRepo,
    ShotgunRepo.type_name: ShotgunRepo,
}


def register_type(repo_cls):
    if repo_cls.type_name not in registry:
        registry[repo_cls.type_name] = repo_cls


def unregister_type(repo_cls):
    registry.pop(repo_cls.type_name, None)
