from datetime import date, timedelta
from typing import List, Set, Dict, Tuple, Optional, Generator

ONE_DAY: timedelta = timedelta(days=1)
QUARTER_START_MONTH: Tuple[int, ...] = (1, 4, 7, 10, 13)

class Date(object):
    """ 
        A date class that provides a number of useful methods to track financial fillings
    """
  
    def __init__(self, date_str: str) -> None:
        """
            Parameters
            ----------
            date_str : str
                The date string in YYYY-MM-DD format
        """
        self.date_inst = date.fromisoformat(date_str) if date_str != None else None
        super().__init__()

    @staticmethod
    def from_date(date_inst: date) -> 'Date':
        date_obj = Date(None)
        date_obj.date_inst = date_inst
        return date_obj

    def __str__(self) -> str:
        """
            Converts this date object into a YYYY-MM-DD string

            Returns
            -------
            str
                the string representation of this date object
        """
        return self.date_inst.__str__()

    def quarter(self) -> int:
        """
            Returns
            -------
            int
                the quarter number 1..4
        """
        return  (self.date_inst.month - 1) // 3 + 1

    def diff_quarters(self, from_date: 'Date') -> int:
        """
            Returns the difference between the quarter number of this date and that of from_date

            Parameters
            ----------
            from_date : Date
                the date from which quarters are counted

            Return
            ------
            int
                the difference between the quarter number of this date and that of from_date
        """
        return self.quarter() - from_date.quarter()

    def diff_days(self, from_date: 'Date') -> int:
        """
            Returns the number of days between this and from_date dates

            Parameters
            ----------
            from_date : Date
                the date from which days are counted

            Return
            ------
            int
                the number of days between this and from_date dates
        """
        delta: timedelta = self.date_inst - from_date.date_inst
        return delta.days + 1

    def quarter_dates(self) -> Tuple[date, date]:
        qbegins: date = None
        for qdate in [date(self.date_inst.year + m // 12, m % 12, 1) for m in QUARTER_START_MONTH]:
            if self.date_inst < qdate:
                return (qbegins, qdate - ONE_DAY)
            qbegins = qdate

    def backfill(self, from_date: 'Date') -> Generator[Tuple[str, int, date, date], None, None]:
        if self.diff_days(from_date) <= 0:
            return

        n_quarters: int = self.diff_quarters(from_date)
        if n_quarters == 0:
            yield ("D", self.diff_days(from_date), from_date.date_inst, self.date_inst)
        else:
            (start_date, end_date) = self.quarter_dates()
            yield("D", None, None, None)
            for q in range(2, n_quarters):
                yield("Q", None, None, None)
                
    def add_days(self, days: int) -> 'Date':
        return Date.from_date(self.date_inst + timedelta(days))
