from edgar_utils.repo.repo_fs import RepoFile, RepoFS
from edgar_utils.date.date_utils import Date

from pathlib import Path
from typing import Dict
import tempfile

class FileRepoDir(object):
    def __init__(self, dir: Path) -> None:
        self.dir = dir
        self.children = {}
        if dir.exists():
            self.build()
        else:
            dir.mkdir()
    
    def exists(self) -> bool:
        return self.dir.exists()

    def children_count(self) -> int:
        return len(self.children)

    def build(self):
        for path in self.dir.iterdir():
            self.children[path.name] = path


class FileRepoFS(RepoFS):
    def __init__(self, base_dir: str) -> None:
        self.base_path : Path = Path(base_dir)
        if not self.base_path.exists():
            self.base_path.mkdir()

        self.d_dir = FileRepoDir(base_dir / "D")
        self.q_dir = FileRepoDir(base_dir / "Q")

    def get_daily_years(self) -> int:
        return len(self.d_dir)
    
    def get_quarterly_file(self, year: int, quarter: int) -> RepoFile:
        pass

    def put_quarterly_file(self, year: int, quarter: int, the_file: RepoFile) -> None:
        pass

    def get_daily_file(self, the_date: Date) -> RepoFile:
        pass

    def put_daily_file(self, the_date: Date, the_file: RepoFile) -> None:
        pass

    def push(self, remote_repo: 'RepoFS') -> None:
        pass

    def pull(self, remote_repo: 'RepoFS') -> None:
        pass