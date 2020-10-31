import pytest, tempfile
from faker import Faker
from pathlib import Path
from edgar_utils.date.date_utils import DatePeriodType
from typing import List
from edgar_utils.tests.globals import YEAR_LIST, QUARTER_LIST, FILE_PER_DIR

@pytest.fixture
def fake():
    fake = Faker()
    return fake

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

@pytest.fixture
def fs_root() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_edgar_repo_fs")
    root: Path = Path(dir.name)
    for t in [DatePeriodType.DAY, DatePeriodType.QUARTER]:
        tdir: Path = root / str(t)
        tdir.mkdir()
        for y in YEAR_LIST:
            ydir: Path = tdir / str(y)
            ydir.mkdir()
            for q in QUARTER_LIST:
                qdir: Path = ydir / q
                qdir.mkdir()
                for i in range(FILE_PER_DIR):
                    file = qdir / "file-{index}.txt".format(index = i)
                    with file.open(mode = "w", buffering = 2048) as fd:
                        fd.write(str(file))
    return dir
