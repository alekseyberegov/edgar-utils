from edgar_utils.repo.repo_fs import RepoFS
from pathlib import Path
from edgar_utils.repo.repo_fs import RepoFS

class Repo(object):
    def __init__(self, repo_fs: RepoFS) -> None:
        self.repo_fs = repo_fs