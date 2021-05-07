from edgar.utils.repo.repo_fs import RepoObject, RepoDir
from pathlib import Path
from typing import Dict, Generator, Iterator, List
import os


class FileRepoObject(RepoObject):
    def __init__(self, parent: RepoDir, obj_name: str) -> None:
        self.__path: Path = parent.path / obj_name
        self.__parent: RepoDir = parent
        parent[obj_name] = self

    def inp(self, bufsize: int) -> Generator[str, None, None]:
        with self.__path.open(mode = "r", buffering=bufsize) as f:
            while True:
                chunk = f.read(bufsize)
                if len(chunk) == 0:
                    break
                yield chunk

    def out(self, iter: Iterator, override: bool = False) -> None:
        file: Path = self.__path if not override else self.__path.with_suffix('.new')
        
        open_flags = (os.O_CREAT | os.O_EXCL | os.O_RDWR)
        open_mode  = 0o644

        handle = os.open(file, open_flags, open_mode)
        with os.fdopen(handle, "w") as f:
            for bytes in iter:
                f.write(bytes)

        if override:
            file.rename(self.__path)

    def subpath(self, levels: int) -> List[str]:
        p: List[str] = self.__parent.subpath(levels - 1) if levels > 1 else []
        p.append(self.__path.name)
        return p
    
    @property
    def path(self) -> Path:
        return self.__path

    @property
    def parent(self) -> RepoDir:
        return self.__parent
    
    def exists(self) -> bool:
        return self.__path.exists()

    def __eq__(self, o: object) -> bool:
       return isinstance(o, FileRepoObject) and self.__path == o.__path

    def __str__(self) -> str:
        return str(self.__path)

