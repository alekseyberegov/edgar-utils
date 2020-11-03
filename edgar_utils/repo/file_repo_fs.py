from sys import path
from edgar_utils.repo.repo_fs import RepoDir, RepoObject, RepoFS, RepoEntity
from edgar_utils.date.date_utils import Date, DatePeriodType
from edgar_utils.date.holidays import USHoliday
from pathlib import Path
from datetime import date
from typing import Dict, Generator, Iterator, Tuple, List, Union
from parse import parse
from calendar import monthrange

import tempfile, os, datetime, abc

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
                if e.name not in self:
                    self[e.name] = FileRepoDir(e, self) if e.is_dir() else FileRepoObject(self, e.name)

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
       return isinstance(o, FileRepoObject) and self.path == o.path


class FileRepoDirVisitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit(object: FileRepoObject) -> bool:
        pass


class FileObjectLocator(object):
    def __init__(self, path: Union[str, List[str]]) -> None:
        self.path = path if isinstance(path, List) else path.split(os.path.sep)

    @staticmethod
    def from_object(obj: FileRepoObject) -> 'FileObjectLocator':
        return FileObjectLocator(obj.subpath(4))

    @staticmethod
    def from_date(date_period: DatePeriodType, the_date: Date, objectname_spec: str) -> 'FileObjectLocator':
        d = the_date.__the_date
        path: List[str] = [
            str(date_period),
            str(d.year),
            str(the_date.quarter()),
            objectname_spec.format(y = d.year, m = d.month, d = d.day)
        ]
        return FileObjectLocator(path)

    def __str__(self) -> str:
        return os.path.sep.join(self.path)

    def __getitem__(self, key):
        return self.path[int(key)]

    def __iter__(self):
        return iter(self.path)

    def year(self) -> int:
        return int(self.path[1])

    def quarter(self) -> int:
        return int(self.path[2][3])

    def date_period(self) -> DatePeriodType:
        return DatePeriodType.from_string(self.path[0])

    def date_object(self, objectname_spec: str) -> Date:
        params = parse(objectname_spec, self.path[3])
        return Date(date(int(params['y']), int(params['m']),int(params['d'])))

    
class FileRepoFS(RepoFS, FileRepoDirVisitor):
    def __init__(self, dir: Path) -> None:
        self.root : FileRepoDir = FileRepoDir(dir)
        self.indices: Dict[str, FileRepoObject] = {}

    def list_years(self, period_type: DatePeriodType) -> List[int]:
        return [int(name) for (name, _) in self.root[str(period_type)]]

    def missing(self, from_date: Date, to_date: Date, objectname_spec: Dict[str,str]) -> List[str]:
        missed: List[str] = []
        self.run_indexing()

        y: int = 0
        q: int = 0
        d: Date = from_date.copy()
        holidays: USHoliday = None
        for i in range(to_date.diff_days(from_date)):
            (c_y, c_q, _, _, _) = d.parts()
            if c_y != y:
                holidays = USHoliday(c_y)
                q = 0
                y = c_y

            if c_q != q:
                loc: str = str(FileObjectLocator.from_date(
                    DatePeriodType.QUARTER, d, objectname_spec[str(DatePeriodType.QUARTER)]))
                if loc not in self.indices:
                    missed.append(loc)
                q = c_y

            if not (d.is_weekend() or d in holidays):
                loc: str = str(FileObjectLocator.from_date(
                    DatePeriodType.DAY, d, objectname_spec[str(DatePeriodType.DAY)]))
                if loc not in self.indices:
                    missed.append(loc)
            d += 1

        return missed

    def get_object(self, rel_path: str) -> RepoObject:
        loc: FileObjectLocator = FileObjectLocator(rel_path)
        e: RepoEntity = self.root
        for i in loc:
            if i in e:
                e = e[i]
            else:
               return None
        return e

    def new_object(self, rel_path: str, objectname: str) -> RepoObject:
        pass

    def run_indexing(self) -> None:
        self.indices.clear()
        self.root.visit(self)

    def visit(self, object: FileRepoObject) -> bool:
        loc: FileObjectLocator = FileObjectLocator.from_object(object)
        self.indices[str(loc)] = object
        return True
