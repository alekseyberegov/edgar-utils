from datetime import date, timedelta
import enum
from typing import List, Set, Dict, Tuple, Optional, Generator
from enum import IntEnum

ONE_DAY: timedelta = timedelta(days=1)
QUARTER_START_MONTH: Tuple[int, ...] = (1, 4, 7, 10, 13)

class BackfillPeriod(IntEnum):
    DAY     = 1,
    QUARTER = 2

    def __str__(self):
        i: int = int(self.value)
        return "DQ"[i - 1 : i]

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
        """
            Create Edgar Date object from a date instance

            Parameters
            ----------
            date_inst: date
                the date instance

            Return
            ------
            Date
                the Edgar Date instance
        """
        date_obj = Date(None)
        date_obj.date_inst = date_inst
        return date_obj

    def __eq__(self, o: object) -> bool:
        another: Date = o
        return another.date_inst == self.date_inst

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

    def quarter_dates(self) -> Tuple['Date', 'Date']:
        """
            Returns a quater to which the Date belongs

            Return
            ------
            Tuple[Date, Date]
                The quarter's start and end dates
        """
        qbegins: date = None
        for qdate in [date(self.date_inst.year + m // 12, m % 12, 1) for m in QUARTER_START_MONTH]:
            if self.date_inst < qdate:
                return (Date.from_date(qbegins), Date.from_date(qdate - ONE_DAY))
            qbegins = qdate

    def backfill(self, from_date: 'Date') -> Generator[Tuple[str, int, 'Date', 'Date'], None, None]:
        """
            Returns backfill periods between from_date and this Date.
            Each period is represented by the following tuple: (period type, days, start date, end date)

            Return
            ------
            Generator[Tuple[str, int, 'Date', 'Date']]
        """
        if self.diff_days(from_date) <= 0:
            return

        qnum: int = self.diff_quarters(from_date)
        (qbeg, qend) = from_date.quarter_dates()

        if qnum == 0:
            yield (BackfillPeriod.QUARTER if from_date == qbeg and self == qend else BackfillPeriod.DAY, 
                self.diff_days(from_date), from_date.date_inst, self.date_inst)
        else:
            yield(BackfillPeriod.QUARTER if from_date == qbeg else BackfillPeriod.DAY, 
                qend.diff_days(from_date), from_date.date_inst, qend.date_inst)

            for q in range(2, qnum + 1):
                (qbeg, qend) = qend.add_days(1).quarter_dates()
                yield(BackfillPeriod.QUARTER, qend.diff_days(qbeg), qbeg, qend)

            (qbeg, qend) = qend.add_days(1).quarter_dates()
            yield(BackfillPeriod.QUARTER if self == qend else BackfillPeriod.DAY, self.diff_days(qbeg), qbeg, self)
                
    def add_days(self, days: int) -> 'Date':
        """
            Create a new Date that has specified number of days added to this Date

            Parameters
            ----------
            days: int
                The number of days to add

            Returns
            -------
            Date
                the new Date (with added days)
        """
        return Date.from_date(self.date_inst + timedelta(days))
