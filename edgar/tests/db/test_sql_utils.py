from edgar.utils.db.sql_utils import insert_sql, table_sql

def test_insert_sql():
    sql: str = insert_sql('mytable', {'a': 1, 'b': 'test'})
    assert sql == "INSERT INTO mytable(a, b) VALUES(1, 'test')"

def test_table_sql():
    sql: str = table_sql('mytable', {'a': 'int', 'b': 'varchar(200)'})
    assert sql == 'CREATE TABLE IF NOT EXISTS mytable(a int, b varchar(200))'