import tempfile
import pytest
from unittest import mock
from pathlib import Path
from typing import Iterator
from edgar.utils.date.date_utils import Date, DatePeriodType
from edgar.utils.repo.repo_pipe import RepoPipe
from edgar.utils.repo.repo_fs import RepoFormat, RepoObject
from edgar.utils.repo.repo_object_path import RepoObjectPath
from edgar.utils.repo.file_repo_fs import FileRepoFS
from edgar.tests.mock import CallTracker

@pytest.fixture
def sink_fs(dir_empty: tempfile.TemporaryDirectory, repo_format: RepoFormat):
    return FileRepoFS(Path(dir_empty.name), repo_format)

@pytest.fixture
def repo_tx():
    tx = mock.MagicMock()
    tx.date_range.return_value = (Date('2021-01-01'), Date('2021-08-01'))
    return tx

@pytest.fixture
def missing(repo_format: RepoFormat) -> Iterator[RepoObjectPath]:
    return iter([
        RepoObjectPath.from_date(DatePeriodType.DAY, Date('2021-07-12'), repo_format),
        RepoObjectPath.from_date(DatePeriodType.DAY, Date('2021-07-13'), repo_format),
        RepoObjectPath.from_date(DatePeriodType.DAY, Date('2021-07-14'), repo_format),
    ])

class TestRepoPipe:
    def test_sync_ndays(self, repo_tx, sink_fs: FileRepoFS, missing: Iterator[RepoObjectPath]) -> None:
        src_fs = mock.MagicMock()
        src_fs.find.side_effect = self.mock_find
        pipe: RepoPipe = RepoPipe(repo_tx, src_fs, sink_fs)

        with mock.patch("edgar.utils.repo.file_repo_fs.FileRepoFS.iterate_missing") as m:
            m.return_value = missing
            pipe.sync()

        for m in missing:
            period_type = m.date_period_type()
            the_date = m.date()
            o: RepoObject = sink_fs.find(period_type, the_date)
            assert ' '.join([str(period_type), str(the_date)]) == next(o.inp(bufsize=1024))
            assert o.exists()

        tracker: CallTracker = CallTracker()
        tracker.add_expected('date_range', [])
        tracker.add_expected('start' , [Date('2021-01-01')])
        tracker.add_expected('create', [DatePeriodType.DAY, Date('2021-07-12')])
        tracker.add_expected('create', [DatePeriodType.DAY, Date('2021-07-13')])
        tracker.add_expected('create', [DatePeriodType.DAY, Date('2021-07-14')])
        tracker.add_expected('commit', [Date('2021-08-01')])
        tracker.assertCalls(repo_tx.mock_calls)

        (beg_date, end_date) = repo_tx.date_range()
        assert sink_fs.find(DatePeriodType.DAY, beg_date) == None
        assert sink_fs.find(DatePeriodType.DAY, end_date) == None

    def mock_find(self, *args, **kwargs):
        obj = mock.MagicMock()
        obj.inp.return_value = iter([str(args[0]), ' ', str(args[1])])
        return obj