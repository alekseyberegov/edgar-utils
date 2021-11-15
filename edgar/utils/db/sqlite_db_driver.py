
from sqlite3 import connect, Cursor, Error
from typing import Dict, List
from functools import reduce
from edgar.utils.db.db_driver import DbDriver


class SqliteDbDriver(DbDriver):
    def __init__(self, db_path: str) -> None:
        self.__db_con = connect(db_path)

    def __del__(self):
        self.__db_con.close()

    def has_table(self, name: str) -> bool:
        cur = self.__db_con.cursor()
        try:
            cur.execute(
                f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{name}'")
            return cur.fetchone()[0] == 1
        finally:
            cur.close()

    @staticmethod
    def new_table_ddl(table_name: str, columns: Dict[str, str]) -> str:
        """
            Generates DDL for creating a new table

            Parameters
            ----------
            table_name:str
                the table name
            columns:Dict[str,str]
                the definition of columns

            Returns
            -------
            str
                SQL for creating new table
        """
        return ' '.join([
                'CREATE TABLE IF NOT EXISTS', table_name,
                '(', ','.join(' '.join(col) for col in columns.items()), ')'
                ])

    @staticmethod
    def new_row_dml(table_name: str, values: Dict) -> str:
        return ' '.join([
            'INSERT INTO', table_name,
            '(', ','.join(n for n in values.keys()), ')'
            'VALUES',
            '(', ','.join(v for v in values.values()), ')'
        ])

    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        sql: str = SqliteDbDriver.new_table_ddl(table_name, columns)
        try:
            self.execute(sql)
            return True
        except Error as _:
            return False

    def fetch_rows(self, table_name: str, limit: int = 100) -> List:
        cur = self.__db_con.cursor()
        try:
            cur.execute(' '.join(['SELECT * FROM', table_name, 'LIMIT', limit]))
            return cur.fetchall()
        finally:
            cur.close()

    def insert_row(self, table_name: str, values: Dict) -> bool:
        sql: str = SqliteDbDriver.new_row_dml(table_name, values)
        try:
            self.execute(sql)
            return True
        except Error as _:
            return False

    def execute(self, stmt: str) -> Cursor:
        """
            Execute the given SQL statement

            Parameters
            ----------
            stmt: str
                SQL statement
        """
        cursor = self.__db_con.cursor()
        try:
            yield cursor.execute(stmt)
        finally:
            cursor.close()
