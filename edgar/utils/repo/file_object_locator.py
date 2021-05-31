from edgar.utils.repo.file_repo_object import FileRepoObject
from edgar.utils.repo.repo_fs import RepoFormatter, RepoFormat
from edgar.utils.date.date_utils import Date, DatePeriodType
from datetime import date
from parse import parse
from typing import Iterator, List, Union
import os


class FileObjectPath(object):
    """
    This class represents an utility that helps locating objects 
    in the repository using either a relative path or date

    Example:
        ["D" | "Q"] / <YEAR> / "QTR"<QUARTER> / "master.idx"
    """

    def __init__(self, path: Union[str, List[str]], repo_format: RepoFormat) -> None:
        """Locate a file object in a repo FS

        Parameters
        -----------
        path: `Union[str,List[str]]`
            the relative path as a string or in a form of a list for individuals path elements
        repo_format: RepoFormat
            the repo format
        """
        self.__path: List[str] = path if isinstance(path, List) else path.split(os.path.sep)
        self.__format: RepoFormat = repo_format

    @staticmethod
    def from_object(obj: FileRepoObject, repo_format: RepoFormat) -> 'FileObjectPath':
        """Get a locator for the given repo object

        Parameters
        ----------
        obj: FileRepoObject
            the repo object for which a locator will be returned
        repo_format: RepoFormat
            the repo format
        
        Returns 
        -------
        FileObjectLocator
            the locator for the given repo object
        """
        return FileObjectPath(obj.subpath(len(repo_format.path_spec) + 1), repo_format)

    @staticmethod
    def from_date(period_type: DatePeriodType, the_date: Date, 
            repo_format: RepoFormat, **kwargs:object) -> 'FileObjectPath':
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
        return FileObjectPath(formatter.format(period_type, the_date, **kwargs), repo_format)

    def __len__(self) -> int:
        """
            Returns the length of the path or object uri

            Returns
            -------
            int
                the length of the path or object uri
        """
        return len(self.__path)

    def __str__(self) -> str:
        """
            Returns a string representation of the path to an object referenced by the locator

            Returns
            -------
            str
                the path to an object referenced by the locator
        """
        return os.path.sep.join(self.__path)

    def __getitem__(self, key):
        """
            Returns the key's element of the locator

            Parameters
            ----------
            key: index or slice

            Returns
            -------
            str
                the key's element of the locator
        """
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.__path)))
            return [self.__path[i] for i in indices]
        else:
            return self.__path[int(key)]

    def __iter__(self) -> Iterator:
        """
            Iterates over the locator's path

            Returns
            -------
            Iterator
                the iterator
        """
        return iter(self.__path)

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
        return int(self.get_param('y'))

    def quarter(self) -> int:
        """
            Returns the quarter number associated with an object identfied by the locator

            Returns
            -------
            int
                the quarter number
        """
        return int(self.get_param('q'))

    def date_period_type(self) -> DatePeriodType:
        """
        Returns the date period associated with an object identified by the locator

        Returns
        -------
        DatePeriodType
            the date period
        """
        return DatePeriodType.from_string(self.get_param('t'))

    def date(self, objectname_spec: str) -> Date:
        """
        Returns the date of the locator

        Parameters
        ----------
        objectname_spec: `str`
            the object name specification

        Returns
        -------
        Date
            the date
        """

        params = parse(objectname_spec, self.__path[-1])
        return Date(date(int(params['y']), int(params['m']),int(params['d'])))

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
        i: int = 0
        macro = '{' + param_name + '}'

        for s in self.__format.path_spec:
            if macro in s:
                return parse(s, self[i])[param_name]
            i += 1
        return None
    