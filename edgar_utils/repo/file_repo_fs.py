from edgar_utils.repo.repo_fs import RepoDir, RepoObject, RepoFS, RepoEntity
from edgar_utils.date.date_utils import Date, DatePeriodType

from pathlib import Path
from typing import Dict, Generator, Iterator, Tuple, List
import tempfile, os, datetime
from unittest.mock import MagicMock

class FileLocked(Exception):
    """File is already locked."""

    def __init__(self, filename, lockfilename):
        self.filename = filename
        self.lockfilename = lockfilename
        super().__init__(filename, lockfilename)


class FileRepoDir(RepoDir):
    def __init__(self, dir: Path, parent: 'FileRepoDir' = None) -> None:
        self.path : Path = dir.resolve()
        self.parent : 'FileRepoDir' = parent
        self.children : Dict[str,RepoEntity] = {}

        if parent is not None:
            self.parent[dir.name] = self

        self.refresh()

        if not self.path.exists():
            self.path.mkdir()
    
    def refresh(self) -> None:
        if self.path.exists():
            for e in self.path.iterdir():
                self[e.name] = FileRepoDir(e) if e.is_dir() else FileRepoObject(self, e.name)

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

    def sorted_objects(self) -> List:
        list = [name for (name, _) in self] 
        return sorted(list, reverse = True)


class FileRepoObject(RepoObject):
    def __init__(self,parent: FileRepoDir, name: str) -> None:
        self.parent: FileRepoDir = parent
        self.name: str = name
        self.path: Path = parent.path / name
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


    def exists(self) -> bool:
        return self.path.exists()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, FileRepoObject):
            return False
        return self.path == o.path


class FileRepoFS(RepoFS):
    def __init__(self, dir: Path) -> None:
        self.root : FileRepoDir = FileRepoDir(dir)
        self.root.new_dir(str(DatePeriodType.DAY))
        self.root.new_dir(str(DatePeriodType.QUARTER))

    def years(self, period_type: DatePeriodType) -> List[int]:
        return [int(name) for (name, _) in self.root[str(period_type)]]

    def latest_dir(self, period_type: DatePeriodType) -> RepoDir:
        pass
    
    def push(self, remote_repo: 'RepoFS') -> None:
        pass

    def pull(self, remote_repo: 'RepoFS') -> None:
        pass