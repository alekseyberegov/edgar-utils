from edgar.utils.repo.repo_fs import RepoObject, RepoDir
from edgar.utils.repo.http_client import HttpClient
from edgar.utils.repo.http_tools import make_url
from typing import List, Iterator

class HttpRepoObject(RepoObject):

    def __init__(self, parent: RepoDir, obj_name: str) -> None:
        self.__url = make_url(parent.as_uri(), obj_name)
        self.__parent: RepoDir = parent
        self.__parent[obj_name] = self

    def as_uri(self) -> str:
        return self.__url

    @property
    def parent(self) -> RepoDir:
        return self.__parent
    
    def subpath(self, levels: int) -> List[str]:
        return self.__url.split("/")[-levels:]

    def exists(self) -> bool:
        client: HttpClient = HttpClient()
        return client.head(self.__url) == 200

    def inp(self, bufsize: int = 2048) -> Iterator[str]:
        client: HttpClient = HttpClient()
        status_code: int = client.get(self.__url)
        yield from client.inp(bufsize=bufsize) if status_code == 200 else ()
        client.close()

    def out(self, iter: Iterator[str], override: bool = False) -> None:
        pass