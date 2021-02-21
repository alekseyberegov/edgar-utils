import pytest, tempfile
from faker import Faker
from pathlib import Path
from datetime import date
from edgar_utils.date.date_utils import Date, DatePeriodType
from typing import List
from edgar_utils.tests.globals import YEAR_LIST, QUARTER_LIST, FILE_PER_DIR, EDGAR_QUARTER

@pytest.fixture
def fake():
    fake = Faker()
    return fake

@pytest.fixture
def dir_empty() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_repo_0")
    return dir

@pytest.fixture
def dir_prepped() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_repo_1")
    root: Path = Path(dir.name)
    for i in YEAR_LIST:
        subdir: Path = root / str(i)
        subdir.mkdir()
    return dir

@pytest.fixture
def test_fs() -> tempfile.TemporaryDirectory:
    dir: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_test_fs")
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

@pytest.fixture
def edgar_fs() -> tempfile.TemporaryDirectory:
    temp: tempfile.TemporaryDirectory  = tempfile.TemporaryDirectory(suffix = "_edgar_fs")
    root: Path = Path(temp.name)
    
    for t in [DatePeriodType.DAY, DatePeriodType.QUARTER]:
        base: Path = root / str(t)
        base.mkdir()

        for s in EDGAR_QUARTER:
            qtr = s.split('-')
            dir: Path = base
            for i in range(2):
                dir = dir / qtr[i]
                dir.mkdir()

            if t == DatePeriodType.QUARTER:
                file: Path = dir / 'master.idx'
                with file.open(mode = "w", buffering = 2048) as fd:
                        fd.write(str(file))
            else:
                dt: Date = Date(date(int(qtr[0]), (int(qtr[1][3]) - 1) * 3 + 1, 1))
                for _ in range(int(qtr[2])):
                    file: Path = dir / dt.format('master{y}{m:02}{d:02}.idx')
                    with file.open(mode = "w", buffering = 2048) as fd:
                        fd.write(str(file))
                    dt.add_days(1)
    return temp

