import tempfile
import pytest
from unittest import mock
from pathlib import Path
from typing import Iterator
from edgar.utils.date.date_utils import Date, DatePeriodType
from edgar.utils.repo.repo_pipe import RepoPipe
from edgar.utils.repo.repo_fs import RepoObject
from edgar.utils.repo.repo_format import RepoObjectPath, RepoFormat
from edgar.utils.repo.file_repo_fs import FileRepoFS
from edgar.tests.mock import CallTracker

@pytest.fixture
def sink_fs(dir_empty: tempfile.TemporaryDirectory, repo_format: RepoFormat):
    return FileRepoFS(Path(dir_empty.name), repo_format)

@pytest.fixture
def repo_ledger():
    tx = mock.MagicMock()
    tx.next_period.return_value = (Date('2021-01-01'), Date('2021-08-01'))
    return tx

@pytest.fixture
def missing(repo_format: RepoFormat) -> Iterator[RepoObjectPath]:
    return iter([
        RepoObjectPath.from_date(DatePeriodType.DAY, Date('2021-07-12'), repo_format),
        RepoObjectPath.from_date(DatePeriodType.DAY, Date('2021-07-13'), repo_format),
        RepoObjectPath.from_date(DatePeriodType.DAY, Date('2021-07-14'), repo_format),
    ])

class TestRepoPipe:
    def test_sync_ndays(self, repo_ledger, sink_fs: FileRepoFS, missing: Iterator[RepoObjectPath]) -> None:
        src_fs = mock.MagicMock()
        src_fs.find.side_effect = self.mock_find
        pipe: RepoPipe = RepoPipe(repo_ledger, src_fs, sink_fs)

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
        tracker.add_expected('next_period', [])
        tracker.add_expected('start' , [Date('2021-01-01')])
        tracker.add_expected('record', [Date('2021-07-12'), DatePeriodType.DAY])
        tracker.add_expected('record', [Date('2021-07-13'), DatePeriodType.DAY])
        tracker.add_expected('record', [Date('2021-07-14'), DatePeriodType.DAY])
        tracker.add_expected('end', [Date('2021-08-01')])
        tracker.assertCalls(repo_ledger.mock_calls)

        (beg_date, end_date) = repo_ledger.next_period()
        assert sink_fs.find(DatePeriodType.DAY, beg_date) == None
        assert sink_fs.find(DatePeriodType.DAY, end_date) == None


    @mock.patch("edgar.utils.repo.file_repo_fs.FileRepoFS.iterate_missing")
    def test_sync_missing_error(self, iterate_missing, repo_ledger, sink_fs: FileRepoFS) -> None:
        src_fs = mock.MagicMock()
        src_fs.find.side_effect = self.mock_find
        error: FileNotFoundError = FileNotFoundError()
        iterate_missing.side_effect = error
        pipe: RepoPipe = RepoPipe(repo_ledger, src_fs, sink_fs)
        pipe.sync()

        tracker: CallTracker = CallTracker()
        tracker.add_expected('next_period', [])
        tracker.add_expected('start', [Date('2021-01-01')])
        tracker.add_expected('error', [None, repr(error)] )
        tracker.assertCalls(repo_ledger.mock_calls)

    @mock.patch("edgar.utils.repo.file_repo_fs.FileRepoFS.create")
    def test_sync_create_error(self, create, repo_ledger, sink_fs: FileRepoFS, missing: Iterator[RepoObjectPath]) -> None:
        with mock.patch("edgar.utils.repo.file_repo_fs.FileRepoFS.iterate_missing") as iterate_missing:
            iterate_missing.return_value = missing
            create.side_effect = self.mock_create
            src_fs = mock.MagicMock()
            src_fs.find.side_effect = self.mock_find

            pipe: RepoPipe = RepoPipe(repo_ledger, src_fs, sink_fs)
            pipe.sync()

        tracker: CallTracker = CallTracker()
        tracker.add_expected('next_period', [])
        tracker.add_expected('start',  [Date('2021-01-01')])
        tracker.add_expected('record', [Date('2021-07-12'), DatePeriodType.DAY])
        tracker.add_expected('error',  [Date('2021-07-13'), repr(FileExistsError())])
        tracker.assertCalls(repo_ledger.mock_calls)

    def mock_find(self, *args, **kwargs):
        obj = mock.MagicMock()
        obj.inp.return_value = iter([str(args[0]), ' ', str(args[1])])
        return obj

    def mock_create(self, *args, **kwargs):
        if str(args[1]) == '2021-07-13':
            raise FileExistsError()
        return mock.MagicMock()