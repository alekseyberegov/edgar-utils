from edgar.utils.repo.repo_fs import RepoFS, RepoObject, RepoTransaction
from edgar.utils.date.date_utils import Date, DatePeriodType

class RepoPipe:
    def __init__(self, trans: RepoTransaction, source: RepoFS, sink: RepoFS) -> None:
        self.__trans = trans
        self.__source = source
        self.__sink = sink

    def sync(self):
        (beg_date, end_date) = self.__trans.date_range()

        for path in self.__sink.iterate_missing(beg_date, end_date):
            the_date: Date = path.date()
            period_type: DatePeriodType = path.date_period_type()
            src_obj: RepoObject = self.__source.find(period_type, the_date)
            dst_obj: RepoObject = self.__sink.create(period_type, the_date)
            dst_obj.out(src_obj.inp(), override=True)
            self.__trans.added(period_type, the_date)

        self.__trans.commit(end_date)
