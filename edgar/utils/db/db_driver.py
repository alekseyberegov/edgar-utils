"""
    The absract driver classes
"""
import abc
from typing import Dict, List

class DbDriver(metaclass=abc.ABCMeta):
    """
        Asbtract database driver
    """
    @abc.abstractmethod
    def has_table(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def create_table(self, name: str, columns: Dict[str, str]) -> bool:
        pass

    @abc.abstractmethod
    def fetch_rows(self, table_name: str, limit: int) -> List:
        pass

    @abc.abstractmethod
    def insert_row(self, table_name: str, values: Dict) -> bool:
        pass

    @abc.abstractmethod
    def close(self) -> None:
        pass
