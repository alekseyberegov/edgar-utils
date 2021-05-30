from edgar.utils.repo.repo_fs import RepoDir, RepoObject
from edgar.utils.repo.http_repo_object import HttpRepoObject
from edgar.utils.repo.http_client import HttpClient
from edgar.utils.repo.http_tools import make_url, norm_dir_url, new_dir_url
from typing import List

class HttpRepoDir(RepoDir):
    def __init__(self, url: str, parent: RepoDir = None) -> None:
        self.__url: str = norm_dir_url(url)
        self.__parent: RepoDir = parent

    def __setitem__(self, key, value):
        pass

    def new_object(self, name: str) -> RepoObject:
        return HttpRepoObject(self, name)

    def new_dir(self, name: str) -> RepoDir:
        return HttpRepoDir(new_dir_url(self.__url, name), self)
    
    def subpath(self, levels: int) -> List[str]:
        return self.__url.rstrip("/").split("/")[-levels:]

    def refresh(self) -> None:
        pass

    def exists(self) -> bool:
        client: HttpClient = HttpClient()
        return client.head(self.__url) == 200

    def as_uri(self) -> str:
        return self.__url
