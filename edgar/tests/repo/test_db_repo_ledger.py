from datetime import datetime
import pytest

from edgar.utils.repo.db_repo_ledger import DbRepoLedger
from edgar.utils.date.date_utils import Date, DatePeriodType

@pytest.fixture(scope="function")
def ledger() -> DbRepoLedger:
    return DbRepoLedger(':memory:')

class TestDbRepoLedger:
    def test_init_db(self, ledger: DbRepoLedger) -> None:
        assert ledger.has_table(DbRepoLedger.REPO_LEDGER_TABLE)

    def test_record(self, ledger: DbRepoLedger) -> None:
        beg_ts: int = int(datetime.now().timestamp())
        ledger.record(Date('2021-11-11'), DatePeriodType.DAY)
        end_ts: int = int(datetime.now().timestamp())
        rows: list = ledger.dump()
        assert len(rows) == 1
        assert rows[0][0] >= beg_ts
        assert rows[0][0] <= end_ts
        assert rows[0][1] == 'record'
        assert rows[0][2] == '2021-11-11'
        assert rows[0][3] == 'D'
        