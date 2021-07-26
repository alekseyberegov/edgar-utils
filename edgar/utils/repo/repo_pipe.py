from edgar.utils.repo.repo_fs import RepoFS, RepoObject, RepoTransaction
from edgar.utils.date.date_utils import Date, DatePeriodType

class RepoPipe:
    def __init__(self, trans: RepoTransaction, source: RepoFS, sink: RepoFS) -> None:
        self.__trans = trans
        self.__source = source
        self.__sink = sink

    def sync(self):
        (beg_date, end_date) = self.__trans.date_range()

        the_date: Date = None
        try:
            self.__trans.start(beg_date)
            for path in self.__sink.iterate_missing(beg_date, end_date):
                the_date = path.date()
                period_type: DatePeriodType = path.date_period_type()
                src_obj: RepoObject = self.__source.find(period_type, the_date)
                dst_obj: RepoObject = self.__sink.create(period_type, the_date)
                dst_obj.out(src_obj.inp(), override=True)
                self.__trans.create(period_type, the_date)
        except Exception as e:
            self.__trans.error(the_date, repr(e))
        else:
            self.__trans.commit(end_date)
