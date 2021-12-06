from contextlib import contextmanager
from sqlite3 import connect, Cursor, Error
from typing import Dict, List
from edgar.utils.db.db_driver import DbDriver

class SqlExecutor:
    def __init__(self) -> None:
        pass
    
    @contextmanager
    def cursor(self, db_con) -> Cursor:
        try:
            cur = db_con.cursor()
            yield cur
        finally:
            cur.close()

class SqliteDbDriver(DbDriver):
    def __init__(self, db_path: str) -> None:
        self.__db_con = connect(db_path)

    def __del__(self):
        self.__db_con.close()

    def has_table(self, name: str) -> bool:
        executor: SqlExecutor = SqlExecutor()
        with executor.cursor(self.__db_con) as cursor:
            cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{name}'")
            return cursor.fetchone()[0] == 1

    @staticmethod
    def new_table_sql(table_name: str, columns: Dict[str, str]) -> str:
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
        return ''.join([
                'CREATE TABLE IF NOT EXISTS ', table_name,
                '(', ', '.join(' '.join(col) for col in columns.items()), ')'
                ])

    @staticmethod
    def new_row_sql(table_name: str, values: Dict) -> str:
        return ''.join([
            'INSERT INTO ', table_name,
            '(', ', '.join(n for n in values.keys()), ') '
            'VALUES',
            '(', ', '.join(str(v) if type(v) in [int,float] else ''.join(['\'',v,'\'']) for v in values.values()), ')'
        ])

    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        sql: str = SqliteDbDriver.new_table_sql(table_name, columns)
        try:
            executor: SqlExecutor = SqlExecutor()
            with executor.cursor(self.__db_con) as cursor:
                cursor.execute(sql)
            return True
        except Error as _:
            return False

    def fetch_rows(self, table_name: str, limit: int = 100) -> List:
        executor: SqlExecutor = SqlExecutor()
        with executor.cursor(self.__db_con) as cursor:
            cursor.execute(' '.join(['SELECT * FROM', table_name, 'LIMIT', str(limit)]))
            return cursor.fetchall()
     
    def insert_row(self, table_name: str, values: Dict) -> bool:
        sql: str = SqliteDbDriver.new_row_sql(table_name, values)
        try:
            executor: SqlExecutor = SqlExecutor()
            with executor.cursor(self.__db_con) as cursor:
                cursor.execute(sql)
            return True
        except Error as e:
            raise e
