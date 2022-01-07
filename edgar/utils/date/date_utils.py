from datetime import date, datetime, timedelta

from typing import List, Set, Dict, Tuple, Optional, Generator, Union
from enum import IntEnum

ONE_DAY: timedelta = timedelta(days=1)
QUARTER_START_MONTH: Tuple[int, ...] = (1, 4, 7, 10, 13)

def to_timestamp() -> int:
    return int(datetime.now().timestamp())

def from_timestamp(ts: int) -> datetime:
    return datetime.fromtimestamp(ts)


class DatePeriodType(IntEnum):
    UNKNOWN = 0
    DAY     = 1
    QUARTER = 2

    def __str__(self):
        return "UDQ"[int(self.value)]

    @staticmethod
    def from_string(code: str) -> 'DatePeriodType':
        return [
            DatePeriodType.UNKNOWN,
            DatePeriodType.DAY,
            DatePeriodType.QUARTER][max(0,"UDQ".find(code))]

class DatePeriodException(Exception):
    pass


class DatePeriod(object):
    def __init__(self, period_type: DatePeriodType, start_date: 'Date', end_date: 'Date') -> None:
        self.period_type = period_type
        self.start_date = start_date
        self.end_date = end_date
        self.num_days = self.end_date.diff_days(self.start_date)

    def expand_to_quarter(self) -> 'DatePeriod':
        (qbeg, qend) = self.start_date.quarter_dates()

        if self.end_date > qend:
            raise DatePeriodException("Can't fit into one quarter: {0} is greater than {1}"
                .format(str(self.end_date), str(qend)))

        self.start_date = qbeg
        self.end_date = qend
        self.period_type = DatePeriodType.QUARTER
        self.num_days = self.end_date.diff_days(self.start_date)

        return self

    def __str__(self) -> str:
        return str(self.period_type) \
            + "," + str(self.start_date) \
            + "," + str(self.end_date) 

    @staticmethod
    def from_string(serialized: str) -> 'DatePeriod':
        s: List[str] = serialized.split(",")
        return DatePeriod(DatePeriodType.from_string(s[0]),  Date(s[1]), Date(s[2]))


class Date(object):
    """ 
        The `Date` class is wrapper around `datetime.date` with a number of useful methods
    """
  
    def __init__(self, the_date: Union[str, date]) -> None:
        """
            Parameters
            ----------
            the_date : str | datetime.date
                The date string in YYYY-MM-DD format or the `datetime.date` object
        """
        self.__the_date = date.fromisoformat(the_date) if isinstance(the_date, str) else the_date

    @staticmethod
    def yesterday() -> 'Date':
        """
            Returns the Date object representing yesterday date

            Return
            ------
            Date
                yesterday
        """
        return Date(date.today() - timedelta(days=1))

    @staticmethod
    def from_date(the_date: date) -> 'Date':
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
        return Date(the_date)

    def format(self, format_spec: str, period_type: DatePeriodType = None, **kwargs: object) -> str:
        """
            Formats the date according to the given specification

            Parameters
            ----------
            format_spec: str
                the formatting specification. Available macros are
                    - {q} for the quarter
                    - {d} for the day number
                    - {m} for the month number
                    - {y} for the 4-digit year number
                    - {t} for the date period type
                    - {i} for the index

            date_period: DatePeriodType
                the date period type

            **kwargs: object
                named arguments to support additional macros

            see https://docs.python.org/3/library/string.html#string-formatting
            
            Return
            ------
            str
                the formatted date
        """
        return format_spec.format(
            q = self.quarter(),
            y = self.__the_date.year,
            m = self.__the_date.month,
            d = self.__the_date.day,
            t = str(period_type) if period_type is not None else '',
            **kwargs
        )

    def tuple(self) -> Tuple[int, int, int, int, int, int]:
        return (
            self.year(),
            self.quarter(),
            self.__the_date.month,
            self.__the_date.day,
            self.isoweekday()
        )

    def __eq__(self, o: object) -> bool:
        """
            Check whether two dates are equal

            Parameters
            ----------
                o: Date
                    the other date with which this date will be compared
        """
        return isinstance(o, Date) and o.__the_date == self.__the_date

    def __lt__(self, o: object) -> bool:
        # Less than	p1 < p2                     p1.__lt__(p2)
        return isinstance(o, Date) and self.__the_date < o.__the_date

    def __le__(self, o: object) -> bool:
        # Less than or equal to                 p1 <= p2 p1.__le__(p2)        
        return isinstance(o, Date) and self.__the_date <= o.__the_date
    
    def __ne__(self, o: object) -> bool:
        # Not equal to	p1 != p2                p1.__ne__(p2)
        return isinstance(o, Date) and self.__the_date != o.__the_date

    def __gt__(self, o: object) -> bool:
        # Greater than	p1 > p2                 p1.__gt__(p2)
        return isinstance(o, Date) and self.__the_date > o.__the_date

    def __ge__(self, o: object) -> bool:
        # Greater than or equal to p1 >= p2     p1.__ge__(p2)
        return isinstance(o, Date) and self.__the_date >= o.__the_date

    def __iadd__(self, o: object):
        return self.add_days(days = int(o))

    def __str__(self) -> str:
        """
            Converts this date object into a YYYY-MM-DD string

            Returns
            -------
            str
                the string representation of this date object
        """
        return self.__the_date.__str__()

    def quarter(self) -> int:
        """
            Return
            ------
            int
                the quarter number between 1 and 4
        """
        return  (self.__the_date.month - 1) // 3 + 1

    def year(self) -> int:
        """
            Returns the year of the date

            Return
            ------
            int
                the year
        """
        return self.__the_date.year

    def isoweekday(self):
        return self.__the_date.isoweekday()

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
                the number of days between this and from_date dates including this date
        """
        delta: timedelta = self.__the_date - from_date.__the_date
        return delta.days + 1

    def quarter_dates(self) -> Tuple['Date', 'Date']:
        """
            Returns a quater in terms of start and end dates to which the Date belongs

            Return
            ------
            Tuple[Date, Date]
                The quarter's start and end dates
        """
        qbegins: date = None
        for qdate in [date(self.__the_date.year + m // 12, m % 12, 1) for m in QUARTER_START_MONTH]:
            if self.__the_date < qdate:
                return (Date.from_date(qbegins), Date.from_date(qdate - ONE_DAY))
            qbegins = qdate

    def backfill(self, from_date: 'Date') -> Generator[DatePeriod, None, None]:
        """
            Returns backfill periods between from_date and this Date.
            Each period is represented by DatePeriod

            Return
            ------
            Generator[DatePeriod]
        """
        if self.diff_days(from_date) <= 0:
            return

        qnum: int = self.diff_quarters(from_date)
        (qbeg, qend) = from_date.quarter_dates()

        if qnum == 0:
            yield DatePeriod(DatePeriodType.QUARTER if from_date == qbeg and self == qend else DatePeriodType.DAY, 
                from_date, self)
        else:
            yield DatePeriod(DatePeriodType.QUARTER if from_date == qbeg else DatePeriodType.DAY, from_date, qend)

            for _ in range(2, qnum + 1):
                (qbeg, qend) = qend.add_days(1).quarter_dates()
                yield DatePeriod(DatePeriodType.QUARTER, qbeg, qend)

            (qbeg, qend) = qend.add_days(1).quarter_dates()
            yield DatePeriod(DatePeriodType.QUARTER if self == qend else DatePeriodType.DAY, qbeg, self)
                
    def copy(self) -> 'Date':
        """
            Creates a copy of this Date instance

            Return
            ------
            Date
                the copy of this Date instance
        """
        return Date(self.__the_date)

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
        self.__the_date = self.__the_date + timedelta(days=days)
        return self
        
    def is_weekend(self) -> bool:
        """
            Indicates whether the current date is weekend

            Return
            ------
                bool
                    True if the current date is weekend; otherwise returns false
        """
        return self.__the_date.isoweekday() in [6, 7]

    def nthday_of_nthweek(self, dayofweek: int, whichweek: int) -> 'Date':
        # get the first day 
        first: date = date(self.__the_date.year, self.__the_date.month, 1)
        # get first dayofweek of the month
        # the formula is "first + 7 - wd(first - n)"
        wd_date = first + timedelta(days = 7 - (first - timedelta(days=dayofweek)).isoweekday())
        the_date = wd_date + timedelta(days=(whichweek - 1) * 7)

        if the_date >= date(first.year + (first.month + 1) // 12, first.month % 12 + 1, 1):
            the_date -= timedelta(7)

        return Date.from_date(the_date)