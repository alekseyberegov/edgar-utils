from edgar_utils.repo.repo_fs import RepoDir, RepoObject, RepoFS, RepoEntity
from edgar_utils.date.date_utils import Date, DatePeriodType

from pathlib import Path
from typing import Dict, Generator, Iterator, Tuple, List
import tempfile, os, datetime
from unittest.mock import MagicMock
import abc

class FileLocked(Exception):
    """File is already locked."""

    def __init__(self, filename, lockfilename):
        self.filename = filename
        self.lockfilename = lockfilename
        super().__init__(filename, lockfilename)


class FileRepoDir(RepoDir):
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
                self[e.name] = FileRepoDir(e, self) if e.is_dir() else FileRepoObject(self, e.name)

    def __iter__(self):
        return iter(self.children.items())

    def __len__(self):
        return len(self.children)

    def __contains__(self, key):
        return key in self.children

    def exists(self) -> bool:
        return self.path.exists()

    def __getitem__(self, key):
        val = self.children[key]
        return val

    def __setitem__(self, key, val):
        self.children[key] = val

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

    def max_entity(self) -> RepoEntity:            
        return self[max([name for (name, _) in self])] if len(self) > 0 else None

    def visit(self, visitor: 'FileRepoDirVisitor') -> None:
        for name in self.sorted_entities():
            o: RepoEntity = self[name]
            if isinstance(o, FileRepoObject):
                if not visitor.visit(o):
                    return False
            else:
                if not o.visit(visitor):
                    return False
        return True



class FileRepoObject(RepoObject):
    def __init__(self, parent: FileRepoDir, name: str) -> None:
        self.path: Path = parent.path / name
        self.parent: FileRepoDir = parent
        parent[name] = self

    def iter_content(self, bufsize: int) -> Generator[str, None, None]:
        with self.path.open(mode = "r", buffering=bufsize) as f:
            while True:
                chunk = f.read(bufsize)
                if len(chunk) == 0:
                    break
                yield chunk

    def write_content(self, iter: Iterator, override: bool = False) -> None:
        file: Path = self.path if not override else self.path.with_suffix('.new')
        
        open_flags = (os.O_CREAT | os.O_EXCL | os.O_RDWR)
        open_mode = 0o644
        handle = os.open(file, open_flags, open_mode)
        with os.fdopen(handle, "w") as f:
            for bytes in iter:
                f.write(bytes)

        if override:
            file.rename(self.path)

    def subpath(self, levels: int) -> List[str]:
        p: List[str] = []
        o: RepoEntity = self
        for _ in range(levels):
            p.insert(0, o.path.name)
            o = o.parent
        return p

    def exists(self) -> bool:
        return self.path.exists()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, FileRepoObject):
            return False
        return self.path == o.path


class FileRepoDirVisitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit(object: FileRepoObject) -> bool:
        pass


class FileRepoFS(RepoFS):
    DEFAULT_START_DATE: Date = Date("2010-01-01")

    def __init__(self, dir: Path, start_date: Date = DEFAULT_START_DATE) -> None:
        self.start_date = start_date
        self.root : FileRepoDir = FileRepoDir(dir)
        self.root.new_dir(str(DatePeriodType.DAY))
        self.root.new_dir(str(DatePeriodType.QUARTER))

    def years(self, period_type: DatePeriodType) -> List[int]:
        return [int(name) for (name, _) in self.root[str(period_type)]]

    def last_object(self, period_type: DatePeriodType) -> Date:
        years: FileRepoDir = self.root[str(period_type)]

        return self.start_date
        