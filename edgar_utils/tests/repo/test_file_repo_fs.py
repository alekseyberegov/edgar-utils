from typing import Dict, Iterator
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

from edgar_utils.repo.file_repo_fs import FileRepoDir, FileRepoObject

YEAR_LIST = [2017, 2018, 2019, 2020]

@pytest.fixture
def dir_empty() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_edgar_repo_0")
    return dir

@pytest.fixture
def dir_prepped() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_edgar_repo_1")
    root: Path = Path(dir.name)
    for i in YEAR_LIST:
        subdir: Path = root / str(i)
        subdir.mkdir()
    return dir

class TestFileRepoDir(object):
    def test_base_dir_empty(self, dir_empty: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        assert repo_dir.exists()
        assert repo_dir.child_count() == 0

    def test_base_dir_prepped(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
   
        subdirs: Dict[str,int] = {}
        for (name, path) in repo_dir:
            subdirs[name] = 1
        
        for i in YEAR_LIST:
            assert str(i) in subdirs
  
    def test_new_object_success(self, dir_empty: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        file_obj: FileRepoObject = repo_dir.new_object("myobject")

        assert file_obj.name == "myobject"
        assert repo_dir.child_count() == 1
        for (_, o) in repo_dir:
            assert o == file_obj

    def test_lastmodified(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        (timestamp, path) = repo_dir.lastmodified()
        now = datetime.today()

        assert path.name == str(max(y for y in YEAR_LIST))
        assert now > timestamp and timestamp > now - timedelta(seconds = 10)

    def test_sorted_objects(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        repo_dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        objects: List = repo_dir.sorted_objects()
        expected: Iterator = iter(sorted(YEAR_LIST, reverse = True))
        for actual in objects:
            assert actual == str(next(expected))


class TestFileRepoFS(object):
    pass