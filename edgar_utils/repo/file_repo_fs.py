from edgar_utils.repo.repo_fs import RepoDir, RepoObject, RepoFS, RepoEntity
from edgar_utils.date.date_utils import Date

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
    def __init__(self, dir: Path) -> None:
        self.path : Path = dir.resolve()
        self.children : Dict[str,RepoEntity] = {}
        
        if self.path.exists():
            for e in self.path.iterdir():
                self.children[e.name] = FileRepoDir(e) if e.is_dir() else FileRepoObject(self, e.name)
        else:
            self.path.mkdir()
    
    def __iter__(self):
        return iter(self.children.items())

    def exists(self) -> bool:
        return self.path.exists()

    def child_count(self) -> int:
        return len(self.children)

    def new_object(self, name: str) -> RepoObject:
        return FileRepoObject(self, name)

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
        parent.children[name] = self

    def iter_content(self, bufsize: int) -> Generator[str, None, None]:
        with self.path.open(mode = "r", buffering=bufsize) as f:
            while True:
                chunk = f.read(bufsize)
                if len(chunk) == 0:
                    break
                yield chunk

    def write_content(self, iter: Iterator) -> None:
        open_flags = (os.O_CREAT | os.O_EXCL | os.O_RDWR)
        open_mode = 0o644
        handle = os.open(self.path, open_flags, open_mode)
        with os.fdopen(handle, "w") as f:
            for bytes in iter:
                f.write(bytes)

    def exists(self) -> bool:
        return self.path.exists()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, FileRepoObject):
            return False
        return self.path == o.path


class FileRepoFS(RepoFS):
    def __init__(self, dir_name: str) -> None:
        self.root : Path = Path(dir_name)
        self.root.resolve()

        if not self.root.exists():
            self.root.mkdir()

        self.d_dir = FileRepoDir(self.root / "D")
        self.q_dir = FileRepoDir(self.root / "Q")

    def get_daily_years(self) -> int:
        return len(self.d_dir)
    
    def get_quarterly_file(self, year: int, quarter: int) -> RepoObject:
        pass

    def put_quarterly_file(self, year: int, quarter: int, the_file: RepoObject) -> None:
        pass

    def get_daily_file(self, the_date: Date) -> RepoObject:
        pass

    def put_daily_file(self, the_date: Date, the_file: RepoObject) -> None:
        pass

    def push(self, remote_repo: 'RepoFS') -> None:
        pass

    def pull(self, remote_repo: 'RepoFS') -> None:
        pass