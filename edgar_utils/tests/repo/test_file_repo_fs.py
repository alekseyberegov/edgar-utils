import pytest
import tempfile
from pathlib import Path

from edgar_utils.repo.file_repo_fs import FileRepoDir

@pytest.fixture
def clean_base_dir() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_edgar_repo")
    return dir

class TestFileRepoDir(object):
    def test_empty_base_dir(self, clean_base_dir) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(clean_base_dir.name))
        assert repo_dir.exists()
        assert repo_dir.children_count() == 0

class TestFileRepoFS(object):
    pass