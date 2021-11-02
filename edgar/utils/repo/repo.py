from edgar.utils.repo.repo_fs import RepoFS

class Repo:
    def __init__(self, repo_fs: RepoFS) -> None:
        self._repo_fs = repo_fs

    @property.getter
    def fs(self) -> RepoFS:
        return self._repo_fs

    @property.setter
    def fs(self, new_fs: RepoFS): # pylint: disable-msg=E0102
        self._repo_fs = new_fs
