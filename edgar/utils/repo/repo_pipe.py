"""
    The classes related to building and managing pipes
"""
from edgar.utils.repo.repo_fs import RepoFS, RepoObject, RepoTransaction
from edgar.utils.date.date_utils import Date, DatePeriodType

class RepoPipe:
    """
        The class represents a pipe between two repositories
        to sync updates in source to sink
    """
    def __init__(self, trans: RepoTransaction, source: RepoFS, sink: RepoFS) -> None:
        self.__trans = trans
        self.__source = source
        self.__sink = sink

    def sync(self):
        """
            Synchronizes source with sync
        """
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
                self.__trans.log(period_type, the_date)
        except Exception as any_exp:
            self.__trans.error(the_date, repr(any_exp))
        else:
            self.__trans.commit(end_date)
