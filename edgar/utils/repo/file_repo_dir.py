from edgar.utils.repo.repo_fs import RepoDir, RepoObject, RepoEntity, RepoDirVisitor
from edgar.utils.repo.file_repo_object import FileRepoObject
from pathlib import Path
from typing import Dict, Tuple, List
import datetime, abc

class FileRepoDir(RepoDir):
    """The repo directory for a regular file system

    Parameters
    ----------
    path : Path
        the physical path to the directory
    parent : RepoDir
        the parent directory
    """
    def __init__(self, path: Path, parent: RepoDir = None) -> None:
        self.__path: Path = path.resolve()
        self.__parent: RepoDir = parent
        self.__children: Dict[str,RepoEntity] = {}

        if parent is not None:
            parent[self.__path.name] = self

        self.refresh()

        if not self.__path.exists():
            self.__path.mkdir()

    def as_uri(self) -> str:
        return self.__path.as_uri()

    @property
    def path(self) -> Path:
        return self.__path

    def refresh(self) -> None:
        if self.__path.exists():
            for e in self.__path.iterdir():
                if e.name not in self:
                    self[e.name] = FileRepoDir(e, self) if e.is_dir() else FileRepoObject(self, e.name)
                else:
                    if e.is_dir(): self[e.name].refresh()

    def __iter__(self):
        return iter(self.__children.items())

    def __len__(self):
        return len(self.__children)

    def __contains__(self, key):
        return key in self.__children

    def __getitem__(self, key):
        val = self.__children[key]
        return val

    def __setitem__(self, key, val):
        self.__children[key] = val

    def exists(self) -> bool:
        return self.__path.exists()

    def new_object(self, name: str) -> RepoObject:
        return FileRepoObject(self, name)

    def new_dir(self, name: str) -> RepoDir:
        return FileRepoDir(self.__path / name, self)

    def tree(self):
        print(f'+ {self.__path}')
        for e in sorted(self.__path.rglob('*')):
            depth = len(e.relative_to(self.__path).parts)
            spacer = '    ' * depth
            print(f'{spacer}+ {e.name}')

    def unique_path(self, name_pattern):
        counter = 0
        while True:
            counter += 1
            e = self.__path / name_pattern.format(counter)
            if not e.exists():
                return e

    def lastmodified(self) -> Tuple[datetime.datetime, Path]:
        (timestamp, file) =  max((f.stat().st_mtime, f) for f in self.__path.iterdir())
        return (datetime.datetime.fromtimestamp(timestamp), file)

    def sort(self) -> List[str]:
        return sorted([name for (name, _) in self], reverse = True) if len(self) > 0 else []

    def get(self, path_list: List[str]) -> RepoEntity:
        o = self
        for i in path_list:
            if i in o:
                o = o[i]
            else:
                return None
        return o

    def visit(self, visitor: RepoDirVisitor) -> None:
        for name in self.sort():
            o: RepoEntity = self[name]
            if isinstance(o, RepoObject):
                if not visitor.visit(o):
                    return False
            else:
                if not o.visit(visitor):
                    return False
        return True

    def subpath(self, levels: int) -> List[str]:
        if levels <= 0:
            return []
        else:
            p = self.__parent.subpath(levels - 1)
            p.append(self.__path.name)
            return p
