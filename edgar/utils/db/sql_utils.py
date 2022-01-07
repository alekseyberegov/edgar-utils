from typing import Dict, Any
from dataclasses import dataclass, field, fields, asdict

def dump_sql(table: str, limit = 100) -> str:
    return ' '.join(['SELECT * FROM', table, 'LIMIT', str(limit)])

def insert_sql(table: str, values: Dict[str,Any]) -> str:
    return ''.join([
            'INSERT INTO ', table,
            '(', ', '.join(c for c in values.keys()), ') '
            'VALUES',
            '(', ', '.join(str(v) \
                if type(v) in [int,float] \
                    else ''.join(['\'',v,'\'']) for v in values.values()), ')'
    ])

def table_sql(table: str, columns: Dict[str, str]) -> str:
    return ''.join([
        'CREATE TABLE IF NOT EXISTS ', table,
        '(', ', '.join(' '.join(col) for col in columns.items()), ')'
    ])

def class_columns(clz) -> Dict[str, str]:
    sql_types: Dict = {int: 'INT', str: 'VARCHAR(128)'}
    return {field.name: sql_types[field.type] for field in fields(clz)}