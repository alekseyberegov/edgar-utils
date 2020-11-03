import pytest
import tempfile

from edgar_utils.repo.repo_fs import RepoEntity
from edgar_utils.date.date_utils import DatePeriodType
from typing import Dict, Iterator, List
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from faker import Faker
from edgar_utils.repo.file_repo_fs import FileRepoDir, FileRepoFS, FileRepoObject
from edgar_utils.tests.globals import YEAR_LIST, YEAR_COUNT, YEAR_MAX, FILE_PER_DIR

class TestFileRepoDir(object):
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
        subdir: Path = dir.path / name
        subdir.mkdir()
        assert len(dir) == len(YEAR_LIST)
        assert name not in dir

        dir.refresh()
        assert len(dir) == len(YEAR_LIST) + 1
        assert name in dir
  
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

    def test_sorted_entities(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        objects: List = dir.sorted_entities()
        expected: Iterator = iter(sorted(YEAR_LIST, reverse = True))
        for actual in objects:
            assert actual == str(next(expected))

    def test_max_entity_exists(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        entity: RepoEntity = dir.max_entity()
        assert entity is not None
        assert entity.path.name == str(max(YEAR_LIST))

    def test_max_entity_none(self, dir_empty: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        assert dir.max_entity() is None

    def test_visit_all_objects(self, fs_root: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(fs_root.name))
        mock: MagicMock = MagicMock()
        mock.visit.return_value = True
        dir.visit(mock)

        i: int = 0
        for c in mock.mock_calls:
            assert c[0] == 'visit'
            assert isinstance(c[1][0], FileRepoObject)
            assert c[1][0].subpath(4) == [
                "QD"[i // (FILE_PER_DIR * 4 * YEAR_COUNT)],
                "{year}".format(year = YEAR_MAX - (i // (FILE_PER_DIR * 4)) % YEAR_COUNT),
                "QTR{quarter}".format(quarter = 4 - (i // FILE_PER_DIR) % 4),
                "file-{file}.txt".format(file = FILE_PER_DIR - (i % FILE_PER_DIR) - 1)
            ]
            i += 1

        assert len(mock.mock_calls) == FILE_PER_DIR * 4 * YEAR_COUNT * 2

    def test_visit_one_object(self, fs_root: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(fs_root.name))
        mock: MagicMock = MagicMock()
        mock.visit.return_value = False
        dir.visit(mock)
        
        c = mock.mock_calls[0]
        assert c[0] == 'visit'
        assert isinstance(c[1][0], FileRepoObject)
        assert c[1][0].subpath(4) == ['Q', str(YEAR_MAX), 'QTR4', 'file-2.txt']
        assert len(mock.mock_calls) == 1


class TestFileRepoObject(object):
    def test_init(self, dir_prepped: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name()
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        obj: FileRepoObject = FileRepoObject(dir, name)

        assert obj.path.name == name
        assert obj.parent == dir
        assert not obj.exists()
        assert name in dir.children
        assert len(dir) == len(YEAR_LIST) + 1

    def test_write_content(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension = 'csv')
        content: List[str] = fake.random_elements(elements=('a', 'b', 'c', 'd'), length=20, unique=False)
        input: MagicMock = MagicMock()
        input.__iter__.return_value = content

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 
        obj.write_content(iter(input))

        assert obj.exists()
        with open(obj.path, "r") as f:
            assert ''.join(content) == f.read()

    def test_write_content_file_exists(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension = 'csv')
        content: List[str] = fake.random_elements(elements=('a', 'b', 'c', 'd'), length=20, unique=False)
        input: MagicMock = MagicMock()
        input.__iter__.return_value = content

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 

        with obj.path.open(mode = "w", buffering = 2048) as f:
            f.write(''.join(content))

        with pytest.raises(FileExistsError): 
            obj.write_content(iter(input))
            raise False
    
    def test_write_content_override(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension = 'csv')
        input: MagicMock = MagicMock()

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 

        input.__iter__.return_value = fake.random_elements(elements=('a', 'b', 'c', 'd'), length=20, unique=False)
        obj.write_content(input)

        input.__iter__.return_value = fake.random_elements(elements=('e', 'f', 'g', 'k'), length=20, unique=False)
        obj.write_content(input, override=True)

        assert obj.exists()
        assert obj.path.name == name
        with open(obj.path, "r") as f:
            assert ''.join(input.__iter__.return_value) == f.read()

    @pytest.mark.parametrize("content_size, chunk_size", [
        (1088,   96),
        (2048,  512),
        (1024, 4096),
        (4096, 4096),
    ])
    def test_iter_content(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker, content_size: int, chunk_size: int) -> None:
        name: str = fake.file_name(extension = 'xml')
        content: str = ''.join(fake.random_elements(elements=('a', 'b', 'c', 'd'), length=content_size, unique=False))

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 

        with obj.path.open(mode = "w", buffering = 2048) as f:
            f.write(content)

        count: int = 0
        result: str = ""
        for chunk in obj.iter_content(chunk_size):
            assert content[count * chunk_size: (count + 1) * chunk_size] == chunk
            result += chunk
            count += 1

        assert count == content_size // chunk_size + (1 if content_size % chunk_size > 0 else 0)
        assert content == result
        
    def test_iter_content_no_file(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, fake.file_name(extension = 'xml')) 

        with pytest.raises(FileNotFoundError):
            for chunk in obj.iter_content(512):
                assert False

class TestFileRepoFS(object):
    def test_list_years(self, fs_root: tempfile.TemporaryDirectory, fake: Faker) -> None:
        fs: FileRepoFS = FileRepoFS(Path(fs_root.name))
        for j in [DatePeriodType.DAY, DatePeriodType.QUARTER]:
            years: List[int] = fs.list_years(j)
            assert max(years) == max(YEAR_LIST)
            for i in YEAR_LIST:
                assert i in years