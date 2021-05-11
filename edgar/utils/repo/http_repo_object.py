from edgar.utils.repo.repo_fs import RepoObject, RepoDir
from urllib.parse import urljoin

class HttpRepoObject(RepoObject):

    def __init__(self, parent: RepoDir, obj_name: str) -> None:
        self.__path = urljoin(parent.path, obj_name)
        self.__parent: RepoDir = parent
        parent[obj_name] = self

    @property
    def path(self):
        return self.__path

    @property
    def parent(self) -> RepoDir:
        return self.__parent
    