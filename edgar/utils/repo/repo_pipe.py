import abc
from edgar.utils.repo.repo_fs import RepoFS
from edgar.utils.date.date_utils import Date

class RepoPipeMeta(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def commit(self, date: Date) -> None:
        pass

    @abc.abstractmethod
    def start_date(self) -> Date:
        pass

class RepoPipe:
    def __init__(self, meta: RepoPipeMeta, source: RepoFS, sink: RepoFS) -> None:
        self.__meta = meta
        self.__source = source
        self.__sink = sink

    def sync(self):
        end_date: Date = Date.yesterday()
        beg_date: Date = self.__meta.start_date()

        for path in self.__sink.iterate_missing(beg_date, end_date):
            pass
