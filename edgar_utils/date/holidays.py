from typing import List, Tuple
from datetime import date
from edgar_utils.date.date_utils import Date

class USHoliday(object):
    FIRST_WEEK: int = 1
    SECOND_WEEK: int = 2
    THIRD_WEEK: int = 3
    FOURTH_WEEK: int = 4
    LAST_WEEK: int = 5

    MONDAY: int = 1
    TUESDAY: int = 2
    WEDNESDAY: int = 3
    THURSDAY: int = 4
    FRIDAY: int = 5
    SATURDAY: int = 6
    SUNDAY: int = 7

    JANUARY: int = 1
    FEBRUARY: int = 2
    MAY: int = 5
    JUNE: int = 6
    JULY: int = 7
    SEPTEMBER: int = 9
    OCTOBER: int = 10
    NOVEMBER: int = 11
    DECEMBER: int = 12

    def __init__(self, year: int) -> None:
        self.list: List[Date] = []

        for i in [
                # New Year              Jan 1
                (self.JANUARY, 1),
                # Independence Day      July 4
                (self.JULY, 4),
                # Veterans Day          Nov 11
                (self.NOVEMBER, 11),
                # Christmas Day         Dec 25
                (self.DECEMBER, 25)
            ]:
            d: Date = Date(date(year, i[0], i[1]))
            self.list.append(d)

        for i in [
                # Martin Luther King, Jr.       third Mon in Jan
                (self.JANUARY, self.MONDAY, self.THIRD_WEEK),
                # Washington's Birthday         third Mon in Feb
                (self.FEBRUARY, self.MONDAY, self.THIRD_WEEK),
                # Memorial Day                  last Mon in May
                (self.MAY, self.MONDAY, self.LAST_WEEK),
                # Labor Day                     first Mon in Sept
                (self.SEPTEMBER, self.MONDAY, self.FIRST_WEEK),
                # Columbus Day                  second Mon in Oct
                (self.OCTOBER, self.MONDAY, self.SECOND_WEEK),
                # Thanksgiving Day              fourth Thur in Nov
                (self.NOVEMBER, self.THURSDAY, self.FOURTH_WEEK),
            ]:
            self.list.append(Date(date(year, i[0], 1)).nthday_of_nthweek(i[1], i[2]))

        for i in self.list:
            wd: int = i.date_inst.isoweekday()
            if wd == self.SATURDAY:
                i.add_days(-1)
            elif wd == self.SUNDAY:
                i.add_days(1)

    def __iter__(self):
        return iter(self.list)

    def __contains__(self, key) -> bool:
        return isinstance(key, Date) and key in self.list

    

 


