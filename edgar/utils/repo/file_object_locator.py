from edgar.utils.repo.file_repo_object import FileRepoObject
from edgar.utils.date.date_utils import Date, DatePeriodType
from datetime import date
from parse import parse
from typing import Iterator, List, Union
import os


class FileObjectLocator(object):
    """
    This class represents an utility that helps locating objects 
    in the repository using either a relative path or date

    The default path specification for objects in the repository is as follow
        ["D" | "Q"] / <YEAR> / "QTR"<QUARTER> 
    """

    DEFAULT_PATH_SPEC: List[str] = ['{t}', '{y}', 'QTR{q}']

    def __init__(self, path: Union[str, List[str]], spec: List[str]) -> None:
        """Locate a file object in a repo FS

        Parameters
        -----------
        path: `Union[str,List[str]]`
            the relative path as a string or in a form of a list for individuals path elements

        spec: `List[str]`
            the path specification
        """
        self.path: List[str] = path if isinstance(path, List) else path.split(os.path.sep)
        self.spec: List[str] = spec

    @staticmethod
    def locate(obj: FileRepoObject, spec: List[str]) -> 'FileObjectLocator':
        """Get a locator for the given repo object

        Parameters
        ----------
        obj: FileRepoObject
            the repo object for which a locator will be returned
        spec : List[str]
            the path specification

        Returns
        -------
        FileObjectLocator
            the locator for the given repo object
        """
        return FileObjectLocator(obj.subpath(len(spec) + 1), spec)

    @staticmethod
    def from_date(date_period: DatePeriodType, the_date: Date, 
            name_spec: str, path_spec: List[str], **kwargs:object) -> 'FileObjectLocator':
        """
        Get an object locator for the given date using the provided name specification

        Parameters
        ----------
        date_period: `DatePeriodType`
            the date period: day or quarter
        the_date: `Date`
            the date
        name_spec: `str`
            the object name specification
        path_spec: `List[str]`
            the object path specification
        **kwargs: object
            extra macros for path and file name templates

        Returns
        -------
        FileObjectLocator
            the file object locator
        """
        return FileObjectLocator([*[the_date.format(spec, date_period, **kwargs) for spec in path_spec], 
            the_date.format(name_spec, date_period, **kwargs)], path_spec)

    def __len__(self) -> int:
        """
            Returns the length of the path or object uri

            Returns
            -------
            int
                the length of the path or object uri
        """
        return len(self.path)

    def __str__(self) -> str:
        """
            Returns a string representation of the path to an object referenced by the locator

            Returns
            -------
            str
                the path to an object referenced by the locator
        """
        return os.path.sep.join(self.path)

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
            indices = range(*key.indices(len(self.path)))
            return [self.path[i] for i in indices]
        else:
            return self.path[int(key)]

    def __iter__(self) -> Iterator:
        """
            Iterates over the locator's path

            Returns
            -------
            Iterator
                the iterator
        """
        return iter(self.path)

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

    def date_period(self) -> DatePeriodType:
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

        params = parse(objectname_spec, self.path[-1])
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

        for s in self.spec:
            if macro in s:
                return parse(s, self[i])[param_name]
            i += 1
        return None
    