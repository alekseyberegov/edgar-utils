import sqlite3
import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from edgar.utils.repo.repo_ledger import RepoLedger
from edgar.utils.date.date_utils import Date, DatePeriodType
from edgar.utils.db.db_driver import DbDriver

def to_timestamp() -> int:
    return int(datetime.datetime.now().timestamp())

def from_timestamp(ts: int) -> datetime:
    return datetime.datetime.fromtimestamp(ts)

@dataclass
class EventObject:
    name: str
    date: str
    data: str = ''
    time: int = field(default_factory=to_timestamp)


class DbRepoLedger(RepoLedger):
    REPO_LEDGER_TABLE : str = 'repo_ledger'

    REPO_LEDGER_ATTRIBUTES: Dict[str, str] = {
        'EVENT_TIME': 'INT',
        'EVENT_NAME': 'VARCHAR(16)',
        'EVENT_DATE': 'VARCHAR(10)',
        'EVENT_DATA': 'VARCHAR(256)'
    }

    def __init__(self, db_driver: DbDriver) -> None:
        self.__db_driver = db_driver
        self.__db_init()

    def __del__(self):
        self.__db_driver.close()

    def __db_init(self) -> None:
        if not self.__db_driver.has_table(DbRepoLedger.REPO_LEDGER_TABLE):
            self.__db_driver.create_table(
                self.REPO_LEDGER_TABLE, self.REPO_LEDGER_ATTRIBUTES)

    def __insert(self, event: EventObject) -> None:
        self.__db_driver.insert_row(self.REPO_LEDGER_TABLE,
            {
                'EVENT_TIME': event.time,
                'EVENT_NAME': event.name,
                'EVENT_DATE': event.date,
                'EVENT_DATA': event.data
            })

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
        return self.__db_driver.fetch_rows(self.REPO_LEDGER_TABLE, limit)
