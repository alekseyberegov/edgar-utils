import sqlite3
import datetime
from dataclasses import dataclass, field
from typing import List, Tuple
from edgar.utils.repo.repo_ledger import RepoLedger
from edgar.utils.date.date_utils import Date, DatePeriodType

def to_timestamp() -> int:
    return int(datetime.datetime.now().timestamp())

def from_timestamp(ts: int) -> datetime:
    return datetime.datetime.fromtimestamp(ts)


@dataclass
class EventObject:
    name: str
    date: str
    data: str = ''
    timestamp: int = field(default_factory=to_timestamp)


class DbRepoLedger(RepoLedger):
    REPO_LEDGER_TABLE : str = 'repo_ledger'

    DDL: str = """
        CREATE TABLE {repo_ledger} (
            RECORD_TIMESTAMP    INT,
            EVENT_NAME          VARCHAR(16),
            EVENT_DATE          VARCHAR(10),
            EVENT_DATA          VARCHAR(256)
        );
    """.format(repo_ledger = REPO_LEDGER_TABLE)

    def __init__(self, db_path: str) -> None:
        self.__db_con = sqlite3.connect(db_path)
        self.__db_init()

    def __del__(self):
        self.__db_con.close()

    def __db_init(self) -> None:
        if not self.has_table(DbRepoLedger.REPO_LEDGER_TABLE):
            cur = self.__db_con.cursor()
            try:
                cur.execute(DbRepoLedger.DDL)
            finally:
                cur.close()

    def has_table(self, table_name: str) -> bool:
        cur = self.__db_con.cursor()
        try:
            cur.execute(
                f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            return cur.fetchone()[0] == 1
        finally:
            cur.close()

    def __insert(self, event: EventObject) -> None:
        cur = self.__db_con.cursor()
        try:
            cur.execute(
            f"""
                INSERT INTO {DbRepoLedger.REPO_LEDGER_TABLE}
                VALUES (
                     {event.timestamp},
                    '{event.name}',
                    '{event.date}',
                    '{event.data}'
                );
            """)
        finally:
            cur.close()

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
        cur = self.__db_con.cursor()
        try:
            cur.execute(f"SELECT * FROM {DbRepoLedger.REPO_LEDGER_TABLE} LIMIT {limit}")
            return cur.fetchall()
        finally:
            cur.close()
