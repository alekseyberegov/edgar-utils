from edgar_utils.repo.repo_fs import RepoFS
from pathlib import Path
from edgar.utils.repo.repo_fs import RepoFS

class Repo(object):
    def __init__(self, repo_fs: RepoFS) -> None:
        self._repo_fs = repo_fs
    
    @property.getter
    def fs(self) -> RepoFS:
        return self._repo_fs

    @property.setter
    def fs(self, new_fs: RepoFS):
        self._repo_fs = new_fs
