from edgar.utils.repo.repo_fs import RepoDir, RepoObject,RepoEntity
from edgar.utils.repo.file_repo_object import FileRepoObject
from pathlib import Path
from typing import Dict, Tuple, List
import datetime, abc

class FileRepoDir(RepoDir):
    """The repo directory for a regular file system

    Parameters
    ----------
    path : `Path`
        the physical path to the directory

    parent : `FileRepoDir`
        the parent directory
    """
    def __init__(self, path: Path, parent: 'FileRepoDir' = None) -> None:
        self.path : Path = path.resolve()
        self.parent : 'FileRepoDir' = parent
        if parent is not None:
            parent[self.path.name] = self

        self.children : Dict[str,RepoEntity] = {}
        self.refresh()

        if not self.path.exists():
            self.path.mkdir()
    
    def refresh(self) -> None:
        if self.path.exists():
            for e in self.path.iterdir():
                if e.name not in self:
                    self[e.name] = FileRepoDir(e, self) if e.is_dir() else FileRepoObject(self, e.name)
                else:
                    if e.is_dir(): self[e.name].refresh()

    def __iter__(self):
        return iter(self.children.items())

    def __len__(self):
        return len(self.children)

    def __contains__(self, key):
        return key in self.children

    def __getitem__(self, key):
        val = self.children[key]
        return val

    def __setitem__(self, key, val):
        self.children[key] = val

    def exists(self) -> bool:
        return self.path.exists()

    def new_object(self, name: str) -> RepoObject:
        return FileRepoObject(self, name)

    def new_dir(self, name: str) -> RepoDir:
        return FileRepoDir(self.path / name, self)

    def tree(self):
        print(f'+ {self.path}')
        for e in sorted(self.path.rglob('*')):
            depth = len(e.relative_to(self.path).parts)
            spacer = '    ' * depth
            print(f'{spacer}+ {e.name}')

    def unique_path(self, name_pattern):
        counter = 0
        while True:
            counter += 1
            e = self.path / name_pattern.format(counter)
            if not e.exists():
                return e

    def lastmodified(self) -> Tuple[datetime.datetime, Path]:
        (timestamp, file) =  max((f.stat().st_mtime, f) for f in self.path.iterdir())
        return (datetime.datetime.fromtimestamp(timestamp), file)

    def sorted_entities(self) -> List[str]:
        return sorted([name for (name, _) in self], reverse = True) if len(self) > 0 else []

    def get(self, path_list: List[str]) -> RepoEntity:
        o = self
        for i in path_list:
            if i in o:
                o = o[i]
            else:
                return None
        return o

    def visit(self, visitor: 'FileRepoDirVisitor') -> None:
        for name in self.sorted_entities():
            o: RepoEntity = self[name]
            if isinstance(o, RepoObject):
                if not visitor.visit(o):
                    return False
            else:
                if not o.visit(visitor):
                    return False
        return True

    def subpath(self, levels: int) -> List[str]:
        p: List[str] = []
        o: RepoEntity = self
        for _ in range(levels):
            p.insert(0, o.path.name)
            o = o.parent
        return p


class FileRepoDirVisitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit(object: RepoObject) -> bool:
        pass

