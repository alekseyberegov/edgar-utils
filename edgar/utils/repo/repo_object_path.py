from edgar.utils.repo.repo_fs import RepoObject
from edgar.utils.repo.repo_fs import RepoFormatter, RepoFormat
from edgar.utils.date.date_utils import Date, DatePeriodType
from datetime import date
from parse import parse
from typing import Iterator, List, Union
import os


class RepoObjectPath(object):
    """
    This class represents an utility that helps locating objects 
    in the repository using either relative path or date

    Examples
    --------
    >>> ["D" | "Q"] / <YEAR> / "QTR"<QUARTER> / "master.idx"
    """

    def __init__(self, repo_format: RepoFormat,
            uri: str = None, 
            list: List[str] = None, 
            period_type: DatePeriodType = None, 
            date: Date = None) -> None:
        """The repo object path

        Parameters
        -----------
        repo_format: RepoFormat
            the repo format
        uri: str
            the URI path
        list: List[str]
            the list of path element
        period_type: DatePeriodType
            the date period type
        date: Date
            the date
        """
        self.__list: List[str] = list if list else uri.split(os.path.sep)
        self.__uri: str = uri if uri else os.path.sep.join(self.__list)
        self.__date: Date = date
        self.__period_type: DatePeriodType = period_type
        self.__format: RepoFormat = repo_format

    @staticmethod
    def from_uri(uri: str, repo_format: RepoFormat) -> 'RepoObjectPath':
        """Create the object path for the given uri

        Parameters
        ----------
        uri: str
            the object relative uri
        """
        return RepoObjectPath(repo_format, uri=uri)

    @staticmethod
    def from_list(list: List[str], repo_format: RepoFormat) -> 'RepoObjectPath':
        return RepoObjectPath(repo_format, list=list)

    @staticmethod
    def from_object(obj: RepoObject, repo_format: RepoFormat) -> 'RepoObjectPath':
        """Get the object path for the given repo object

        Parameters
        ----------
        obj: RepoObject
            the repo object for which a locator will be returned
        repo_format: RepoFormat
            the repo format
        
        Returns 
        -------
        FileObjectLocator
            the locator for the given repo object
        """
        return RepoObjectPath(repo_format, list=obj.subpath(len(repo_format.path_spec) + 1))

    @staticmethod
    def from_date(period_type: DatePeriodType, the_date: Date, 
            repo_format: RepoFormat, **kwargs:object) -> 'RepoObjectPath':
        """
        Get an object locator for the given date using the provided name specification

        Parameters
        ----------
        date_period: `DatePeriodType`
            the date period type: day or quarter
        the_date: `Date`
            the date
        repo_format: RepoFormat
            the repo format
        **kwargs: object
            extra macros for path and file name templates

        Returns
        -------
        FileObjectLocator
            the file object locator
        """
        formatter: RepoFormatter = RepoFormatter(repo_format)
        return RepoObjectPath(repo_format, 
            list=formatter.format(period_type, the_date, **kwargs),
            period_type=period_type,
            date=the_date)

    def __len__(self) -> int:
        """
            Returns the length of the path or object uri

            Returns
            -------
            int
                the length of the path or object uri
        """
        return len(self.__list)

    def __str__(self) -> str:
        """
            Returns a string representation of the path to an object referenced by the locator

            Returns
            -------
            str
                the path to an object referenced by the locator
        """
        return self.__uri

    def __getitem__(self, key):
        """
            Returns the key's element of the object path

            Parameters
            ----------
            key: index or slice

            Returns
            -------
            str
                the key's element of the object path
        """
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.__list)))
            return [self.__list[i] for i in indices]
        else:
            return self.__list[int(key)]

    def __iter__(self) -> Iterator:
        """
            Iterates over the object path's elements

            Returns
            -------
            Iterator
                the iterator
        """
        return iter(self.__list)

    def parent(self) -> str:
        """
            Returns the parent path

            Returns
            -------
            the parent path
        """
        return os.path.sep.join(self[:-1])

    def year(self) -> int:
        """
            Returns the year number associated with an object identified by the locator

            Returns
            -------
            int
                the year number
        """
        return self.__date.year() if self.__date else self.date().year()

    def quarter(self) -> int:
        """
            Returns the quarter number associated with an object identfied by the locator

            Returns
            -------
            int
                the quarter number
        """
        return self.__date.quarter() if self.__date else self.date().quarter()

    def date_period_type(self) -> DatePeriodType:
        """
        Returns the date period associated with an object identified by the locator

        Returns
        -------
        DatePeriodType
            the date period
        """
        if not self.__period_type:
            self.__period_type = DatePeriodType.from_string(self.get_param('t'))
        
        return self.__period_type

    def date(self) -> Date:
        """
        Returns the date for an object at the object path

        Returns
        -------
        Date
            the date
        """
        if not self.__date:
            params = parse(self.__format.name_spec[DatePeriodType.DAY], self.__list[-1])
            self.__date = Date(date(int(params['y']), int(params['m']),int(params['d'])))

        return self.__date

    def get_param(self, param_name: str) -> str:
        """
            Parses year/quarter/period from the locator

            Parameters
            ----------
            param_name
                the parameter name: q - quarter; y - year; d - date period

            Returns
            -------
            str
                the parameter value if the parameter is found; otherwise returns None
        """
        macro = '{' + param_name + '}'

        for i, s in enumerate(self.__format.path_spec):
            if macro in s:
                return parse(s, self[i])[param_name]
        return None
