import pytest, tempfile

from pathlib import Path
from faker import Faker
from unittest.mock import MagicMock
from typing import List
from edgar.utils.repo.file_repo_dir import FileRepoDir
from edgar.utils.repo.file_repo_object import FileRepoObject
from edgar.tests.globals import YEAR_LIST

class TestFileRepoObject(object):
    def test_init(self, dir_prepped: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name()
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        obj: FileRepoObject = FileRepoObject(dir, name)

        assert obj.path.name == name
        assert obj.parent == dir
        assert not obj.exists()
        assert name in dir
        assert len(dir) == len(YEAR_LIST) + 1

    def test_out(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension = 'csv')
        content: List[str] = fake.random_elements(elements=('a', 'b', 'c', 'd'), length=20, unique=False)
        input: MagicMock = MagicMock()
        input.__iter__.return_value = content

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 
        obj.out(iter(input))

        assert obj.exists()
        with open(obj.path, "r") as f:
            assert ''.join(content) == f.read()

    def test_out_file_exists(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension = 'csv')
        content: List[str] = fake.random_elements(elements=('a', 'b', 'c', 'd'), length=20, unique=False)
        input: MagicMock = MagicMock()
        input.__iter__.return_value = content

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 

        with obj.path.open(mode = "w", buffering = 2048) as f:
            f.write(''.join(content))

        with pytest.raises(FileExistsError): 
            obj.out(iter(input))
            assert False
    
    def test_out_overwrite(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension = 'csv')
        input: MagicMock = MagicMock()

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 

        input.__iter__.return_value = fake.random_elements(elements=('a', 'b', 'c', 'd'), length=20, unique=False)
        obj.out(input)

        input.__iter__.return_value = fake.random_elements(elements=('e', 'f', 'g', 'k'), length=20, unique=False)
        obj.out(input, override=True)

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
    def test_inp(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker, content_size: int, chunk_size: int) -> None:
        name: str = fake.file_name(extension = 'xml')
        content: str = ''.join(fake.random_elements(elements=('a', 'b', 'c', 'd'), length=content_size, unique=False))

        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, name) 

        with obj.path.open(mode = "w", buffering = 2048) as f:
            f.write(content)

        count: int = 0
        result: str = ""
        for chunk in obj.inp(chunk_size):
            assert content[count * chunk_size: (count + 1) * chunk_size] == chunk
            result += chunk
            count += 1

        assert count == content_size // chunk_size + (1 if content_size % chunk_size > 0 else 0)
        assert content == result
        
    def test_inp_no_file(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = FileRepoObject(dir, fake.file_name(extension = 'xml')) 

        with pytest.raises(FileNotFoundError):
            for chunk in obj.inp(512):
                assert False
