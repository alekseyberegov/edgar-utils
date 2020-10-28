from typing import Dict
import pytest
import tempfile
from pathlib import Path

from edgar_utils.repo.file_repo_fs import FileRepoDir, FileRepoObject

@pytest.fixture
def clean_base_dir() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_edgar_repo_0")
    return dir

@pytest.fixture
def base_dir() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_edgar_repo_1")
    root: Path = Path(dir.name)
    for i in [2017, 2018, 2019, 2020]:
        subdir: Path = root / str(i)
        subdir.mkdir()
    return dir

class TestFileRepoDir(object):
    def test_empty_base_dir(self, clean_base_dir: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(clean_base_dir.name))
        assert repo_dir.exists()
        assert repo_dir.child_count() == 0

    def test_build_success(self, base_dir: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(base_dir.name))
   
        subdirs: Dict[str,int] = {}
        for (name, path) in repo_dir:
            subdirs[name] = 1
        
        assert "2017" in subdirs
        assert "2018" in subdirs
        assert "2019" in subdirs
        assert "2020" in subdirs

    def test_new_object_success(self,  clean_base_dir: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(clean_base_dir.name))
        file_obj: FileRepoObject = repo_dir.new_object("myobject")

        assert file_obj.name == "myobject"
        assert repo_dir.child_count() == 1

        for (_, o) in repo_dir:
            assert o == file_obj




class TestFileRepoFS(object):
    pass