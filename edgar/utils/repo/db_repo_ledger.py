from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple
from edgar.utils.repo.repo_ledger import RepoLedger
from edgar.utils.date.date_utils import Date, DatePeriodType, to_timestamp
from edgar.utils.db.db_driver import DbDriver
from edgar.utils.db.sql_utils import class_columns

@dataclass
class EventObject:
    event_name: str
    event_date: str
    event_data: str = ''
    event_time: int = field(default_factory=to_timestamp)


class DbRepoLedger(RepoLedger):
    TABLE_NAME : str = 'repo_ledger'

    def __init__(self, db_driver: DbDriver) -> None:
        self.__db_driver = db_driver
        self.__db_init()

    def __del__(self):
        self.__db_driver.close()

    def __db_init(self) -> None:
        if not self.__db_driver.has_table(DbRepoLedger.TABLE_NAME):
            self.__db_driver.create_table(self.TABLE_NAME, class_columns(EventObject))

    def __insert(self, event: EventObject) -> None:
        self.__db_driver.insert_row(self.TABLE_NAME, asdict(event))

    def start(self, date: Date) -> None:
        self.__insert(EventObject('start', str(date)))

    def end(self, date: Date) -> None:
        self.__insert(EventObject('end', str(date)))

    def error(self, date: Date, error: str) -> None:
        self.__insert(EventObject('error', str(date), error))

    def record(self, date: Date, period_type: DatePeriodType) -> None:
        self.__insert(EventObject('record', str(date), str(period_type)))

    def next_period(self) -> Tuple[Date,Date]:
        pass

    def dump(self, limit: int = 10) -> List:
        return self.__db_driver.fetch_rows(self.TABLE_NAME, limit)
