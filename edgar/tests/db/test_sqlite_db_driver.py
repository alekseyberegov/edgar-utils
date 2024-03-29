import pytest
from typing import List
from sqlite3 import Error
from edgar.utils.db.sqlite_db_driver import SqliteDbDriver

@pytest.fixture(scope="function")
def db_driver() -> SqliteDbDriver:
    return SqliteDbDriver(':memory:')

class TestSqliteDbDriver:
    def test_has_table_false(self, db_driver: SqliteDbDriver) -> None:
        assert not db_driver.has_table('mytable')

    def test_has_table_true(self, db_driver: SqliteDbDriver) -> None:
        assert db_driver.create_table('mytable', {'a': 'int', 'b': 'varchar(200)'})
        assert db_driver.has_table   ('mytable')

    def test_insert_row_success(self, db_driver: SqliteDbDriver) -> None:
        assert db_driver.create_table('mytable', {'a': 'int', 'b': 'varchar(200)'})
        assert db_driver.insert_row  ('mytable', {'a': 10000, 'b': 'hello driver'})
        rows: List = db_driver.fetch_rows('mytable')
        assert rows[0][0] == 10000
        assert rows[0][1] == 'hello driver'

    def test_insert_row_fail(self, db_driver: SqliteDbDriver) -> None:
        assert db_driver.create_table('mytable', {'a': 'int', 'b': 'varchar(200)'})
        with pytest.raises(Error):
            db_driver.insert_row('wrong', {'a': 10000, 'b': 'hello driver'})