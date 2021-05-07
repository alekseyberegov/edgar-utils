from typing import List, Dict
from datetime import date
from edgar.utils.date.date_utils import Date

# https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/#url=2020
# This holiday is designated as "Washington’s Birthday" in section 6103(a) of title 5 of the United States Code, which is the
# law that specifies holidays for Federal employees. Though other institutions such as state and local governments and private
# businesses may use other names, it is our policy to always refer to holidays by the names designated in the law.

class us_holidays(object):
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
        self.names: Dict[str,str] = {}

        for i in [
                # New Year              Jan 1
                (self.JANUARY, 1, 'New Year''s Day'),
                # Independence Day      July 4
                (self.JULY, 4, 'Independency Day'),
                # Veterans Day          Nov 11
                (self.NOVEMBER, 11, 'Veterans Day'),
                # Christmas Day         Dec 25
                (self.DECEMBER, 25, 'Christmas Day')
            ]:
            d: Date = Date(date(year, i[0], i[1]))
            self.names[str(d)] = i[2]
            self.list.append(d)

        for i in [
                # Martin Luther King, Jr.       third Mon in Jan
                (self.JANUARY, self.MONDAY, self.THIRD_WEEK, 'Birthday of Martin Luther King, Jr.'),
                # Washington's Birthday         third Mon in Feb
                (self.FEBRUARY, self.MONDAY, self.THIRD_WEEK, 'Washington''s Birthday'),
                # Memorial Day                  last Mon in May
                (self.MAY, self.MONDAY, self.LAST_WEEK, 'Memorial Day'),
                # Labor Day                     first Mon in Sept
                (self.SEPTEMBER, self.MONDAY, self.FIRST_WEEK, 'Labor Day'),
                # Columbus Day                  second Mon in Oct
                (self.OCTOBER, self.MONDAY, self.SECOND_WEEK, 'Columbus Day'),
                # Thanksgiving Day              fourth Thur in Nov
                (self.NOVEMBER, self.THURSDAY, self.FOURTH_WEEK, 'Thanksgiving Day'),
            ]:
            d: Date = Date(date(year, i[0], 1)).nthday_of_nthweek(i[1], i[2])
            self.names[str(d)] = i[3]
            self.list.append(d)

        for i in self.list:
            wd: int = i.isoweekday()
            if wd == self.SATURDAY:
                i += -1
            elif wd == self.SUNDAY:
                i += 1

    def __iter__(self):
        return iter(self.list)

    def __len__(self):
        return len(self.list)

    def __contains__(self, key) -> bool:
        return isinstance(key, Date) and key in self.list

    def __lshift__(self, the_date):
        s: str = str(the_date)
        return self.names[s] if s in self.names else ''

    

 


