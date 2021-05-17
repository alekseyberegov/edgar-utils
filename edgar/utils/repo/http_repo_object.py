from edgar.utils.repo.repo_fs import RepoObject, RepoDir
from edgar.utils.repo.http_client import HttpClient
from urllib.parse import urljoin
from typing import List, Iterator

class HttpRepoObject(RepoObject):

    def __init__(self, parent: RepoDir, obj_name: str) -> None:
        self.__url = urljoin(parent.as_uri(), obj_name)
        self.__parent: RepoDir = parent
        parent[obj_name] = self

    def as_url(self) -> str:
        return self.__url

    @property
    def parent(self) -> RepoDir:
        return self.__parent
    
    def subpath(self, levels: int) -> List[str]:
        return self.__url.split("/")[-levels:]

    def exists(self) -> bool:
        client: HttpClient = HttpClient()
        return client.head(self.__url) == 200

    def inp(self, bufsize: int) -> Iterator[str]:
        client: HttpClient = HttpClient()
        if client.get(self.__url) == 200:
            return client.inp(bufsize=bufsize)
        else:
            client.close()
            yield from ()

    def out(self, iter: Iterator[str], override: bool = False) -> None:
        pass