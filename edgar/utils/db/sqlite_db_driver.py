from contextlib import contextmanager
from sqlite3 import connect, Cursor, Error, Connection
from typing import Dict, List
from edgar.utils.db.db_driver import DbDriver
from edgar.utils.db.sql_utils import dump_sql, insert_sql, table_sql

class Executor:
    def __init__(self) -> None:
        pass

    @contextmanager
    def cursor(self, con: Connection) -> Cursor:
        try:
            cur = con.cursor()
            yield cur
        finally:
            cur.close()

class SqliteDbDriver(DbDriver):
    def __init__(self, db_path: str) -> None:
        self.__con: Connection = connect(db_path)
        self.__run: Executor = Executor()

    def __del__(self):
        self.__con.close()

    def has_table(self, name: str) -> bool:
        with self.__run.cursor(self.__con) as cursor:
            cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{name}'")
            return cursor.fetchone()[0] == 1

    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        try:
            with self.__run.cursor(self.__con) as cursor:
                cursor.execute(table_sql(table_name, columns))
            return True
        except Error as _:
            return False

    def fetch_rows(self, table_name: str, limit: int = 100) -> List:
        with self.__run.cursor(self.__con) as cursor:
            cursor.execute(dump_sql(table_name, limit))
            return cursor.fetchall()

    def insert_row(self, table_name: str, values: Dict) -> bool:
        with self.__run.cursor(self.__con) as cursor:
            cursor.execute(insert_sql(table_name, values))
            return True

    def close(self) -> None:
        self.__con.close()
