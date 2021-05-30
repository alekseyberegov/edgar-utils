import pytest, tempfile, unittest

from faker import Faker
from unittest.mock import MagicMock
from pathlib import Path
from typing import Dict, List, Iterator
from datetime import datetime, timedelta
from edgar.utils.repo.file_repo_object import FileRepoObject
from edgar.utils.repo.file_repo_dir import FileRepoDir
from edgar.tests.globals import YEAR_LIST, FILE_PER_DIR


class TestFileRepoDir:
    def test_init_dir_empty(self, dir_empty: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        assert dir.exists()
        assert len(dir) == 0

    def test_init_dir_prepped(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
   
        subdirs: Dict[str,int] = {}
        for (name, _) in dir:
            subdirs[name] = 1
        
        for i in YEAR_LIST:
            assert str(i) in subdirs

    def test_refresh(self, dir_prepped: tempfile.TemporaryDirectory, fake: Faker) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        assert len(dir) == len(YEAR_LIST)

        name: str = fake.file_name()
        path: Path = dir.path / name
        path.mkdir()

        for i in range(2):
            assert len(dir) == len(YEAR_LIST) + i
            assert (lambda x: (x == 0 and name not in dir) or (x == 1 and name in dir))(i)
            dir.refresh()
  
    def test_new_object_success(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name()
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = dir.new_object(name)

        assert obj.path.name == name
        assert len(dir) == 1
        for (_, o) in dir:
            assert o == obj

    def test_new_dir_success(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension="")
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        subdir = dir.new_dir(name)

        assert len(dir) == 1
        assert name in dir
        assert subdir.exists()

    def test_lastmodified(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        (timestamp, path) = dir.lastmodified()
        now = datetime.today()

        assert path.name == str(max(y for y in YEAR_LIST))
        assert now > timestamp and timestamp > now - timedelta(seconds = 10)

    def test_sort(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        objects: List[str] = dir.sort()
        expected: Iterator = iter(sorted(YEAR_LIST, reverse = True))
        for actual in objects:
            assert actual == str(next(expected))

    @pytest.mark.parametrize("path_list, expected_path", [
        (['Q', '2020', 'QTR1', 'file-0.txt'],  'Q/2020/QTR1/file-0.txt' ),
        (['Q', '2020', 'QTR3', 'file-1.txt'],  'Q/2020/QTR3/file-1.txt' ),
    ])
    def test_get_success(self, test_fs: tempfile.TemporaryDirectory, path_list: List[str], expected_path: str):
        root: Path = Path(test_fs.name)
        dir: FileRepoDir = FileRepoDir(root)
        obj: FileRepoObject = dir.get(path_list)
        assert  (root / expected_path).resolve() == obj.path

    @pytest.mark.parametrize("path_list", [
        (['Q', '2200', 'QTR1', 'file-0.txt']),
        (['Q', '2020', 'QTR3', 'file-9.txt']),
    ])
    def test_get_failure(self, test_fs: tempfile.TemporaryDirectory, path_list: List[str]):
        root: Path = Path(test_fs.name)
        dir: FileRepoDir = FileRepoDir(root)
        obj: FileRepoObject = dir.get(path_list)
        assert  obj is None


    def test_visit_all_objects(self, test_fs: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(test_fs.name))
        mock: MagicMock = MagicMock()
        mock.visit.return_value = True
        dir.visit(mock)

        l: int = len(YEAR_LIST)
        m: int = max(YEAR_LIST)
        i: int = 0
        for c in mock.mock_calls:
            assert c[0] == 'visit'
            assert isinstance(c[1][0], FileRepoObject)
            assert c[1][0].subpath(4) == [
                "QD"[i // (FILE_PER_DIR * 4 * l)],
                "{year}".format(year = m - (i // (FILE_PER_DIR * 4)) % l),
                "QTR{quarter}".format(quarter = 4 - (i // FILE_PER_DIR) % 4),
                "file-{file}.txt".format(file = FILE_PER_DIR - (i % FILE_PER_DIR) - 1)
            ]
            i += 1

        assert len(mock.mock_calls) == FILE_PER_DIR * 4 * l * 2

    def test_visit_one_object(self, test_fs: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(test_fs.name))
        mock: MagicMock = MagicMock()
        mock.visit.return_value = False
        dir.visit(mock)
        
        c = mock.mock_calls[0]
        assert c[0] == 'visit'
        assert isinstance(c[1][0], FileRepoObject)
        assert c[1][0].subpath(4) == ['Q', str(max(YEAR_LIST)), 'QTR4', 'file-2.txt']
        assert len(mock.mock_calls) == 1

