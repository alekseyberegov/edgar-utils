from sys import path
from edgar_utils.repo.repo_fs import RepoDir, RepoObject, RepoFS, RepoEntity, RepoFormat
from edgar_utils.date.date_utils import Date, DatePeriodType
from edgar_utils.date.holidays import USHoliday
from pathlib import Path
from datetime import date
from typing import Dict, Generator, Iterator, Tuple, List, Union
from parse import parse

import os, datetime, abc

class FileLocked(Exception):
    """File is already locked."""

    def __init__(self, filename, lockfilename):
        self.filename = filename
        self.lockfilename = lockfilename
        super().__init__(filename, lockfilename)


class FileRepoDir(RepoDir):
    def __init__(self, path: Path, parent: 'FileRepoDir' = None) -> None:
        self.path : Path = path.resolve()
        self.parent : 'FileRepoDir' = parent
        if parent is not None:
            parent[self.path.name] = self

        self.children : Dict[str,RepoEntity] = {}
        self.refresh()

        if not self.path.exists():
            self.path.mkdir()
    
    def refresh(self) -> None:
        if self.path.exists():
            for e in self.path.iterdir():
                if e.name not in self:
                    self[e.name] = FileRepoDir(e, self) if e.is_dir() else FileRepoObject(self, e.name)
                else:
                    if e.is_dir(): self[e.name].refresh()

    def __iter__(self):
        return iter(self.children.items())

    def __len__(self):
        return len(self.children)

    def __contains__(self, key):
        return key in self.children

    def __getitem__(self, key):
        val = self.children[key]
        return val

    def __setitem__(self, key, val):
        self.children[key] = val

    def exists(self) -> bool:
        return self.path.exists()

    def new_object(self, name: str) -> RepoObject:
        return FileRepoObject(self, name)

    def new_dir(self, name: str) -> RepoDir:
        return FileRepoDir(self.path / name, self)

    def tree(self):
        print(f'+ {self.path}')
        for e in sorted(self.path.rglob('*')):
            depth = len(e.relative_to(self.path).parts)
            spacer = '    ' * depth
            print(f'{spacer}+ {e.name}')

    def unique_path(self, name_pattern):
        counter = 0
        while True:
            counter += 1
            e = self.path / name_pattern.format(counter)
            if not e.exists():
                return e

    def lastmodified(self) -> Tuple[datetime.datetime, Path]:
        (timestamp, file) =  max((f.stat().st_mtime, f) for f in self.path.iterdir())
        return (datetime.datetime.fromtimestamp(timestamp), file)

    def sorted_entities(self) -> List[str]:
        return sorted([name for (name, _) in self], reverse = True) if len(self) > 0 else []

    def get(self, path_list: List[str]) -> RepoEntity:
        o = self
        for i in path_list:
            if i in o:
                o = o[i]
            else:
                return None
        return o

    def visit(self, visitor: 'FileRepoDirVisitor') -> None:
        for name in self.sorted_entities():
            o: RepoEntity = self[name]
            if isinstance(o, FileRepoObject):
                if not visitor.visit(o):
                    return False
            else:
                if not o.visit(visitor):
                    return False
        return True

    def subpath(self, levels: int) -> List[str]:
        p: List[str] = []
        o: RepoEntity = self
        for _ in range(levels):
            p.insert(0, o.path.name)
            o = o.parent
        return p

class FileRepoObject(RepoObject):
    def __init__(self, parent: FileRepoDir, name: str) -> None:
        self.path: Path = parent.path / name
        self.parent: FileRepoDir = parent
        parent[name] = self

    def iter_content(self, bufsize: int) -> Generator[str, None, None]:
        with self.path.open(mode = "r", buffering=bufsize) as f:
            while True:
                chunk = f.read(bufsize)
                if len(chunk) == 0:
                    break
                yield chunk

    def write_content(self, iter: Iterator, override: bool = False) -> None:
        file: Path = self.path if not override else self.path.with_suffix('.new')
        
        open_flags = (os.O_CREAT | os.O_EXCL | os.O_RDWR)
        open_mode  = 0o644

        handle = os.open(file, open_flags, open_mode)
        with os.fdopen(handle, "w") as f:
            for bytes in iter:
                f.write(bytes)

        if override:
            file.rename(self.path)

    def subpath(self, levels: int) -> List[str]:
        p: List[str] = self.parent.subpath(levels - 1) if levels > 1 else []
        p.append(self.path.name)
        return p

    def exists(self) -> bool:
        return self.path.exists()

    def __eq__(self, o: object) -> bool:
       return isinstance(o, FileRepoObject) and self.path == o.path

    def __str__(self) -> str:
        return str(self.path)


class FileRepoDirVisitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit(object: FileRepoObject) -> bool:
        pass


class FileObjectLocator(object):
    """
        This class represents an utility that helps locating objects in the repository
        using either a relative path or date
    """

    """
        The default path specification for objects in the repository
            ["D" | "Q"] / <YEAR> / "QTR"<QUARTER> 
    """
    DEFAULT_PATH_SPEC: List[str] = ['{t}', '{y}', 'QTR{q}']

    """
        Locate a file object in a repo FS

        Parameters
        ----------
        path: Union[str,List[str]]
            a relative path as a string or in a form of a list for individuals path elements
        spec: List[str]
            the path specification
    """
    def __init__(self, path: Union[str, List[str]], spec: List[str]) -> None:
        self.path = path if isinstance(path, List) else path.split(os.path.sep)
        self.spec = spec

    @staticmethod
    def locate(obj: FileRepoObject, path_spec: List[str]) -> 'FileObjectLocator':
        """
            Get a locator for the given repo object

            Parameters
            ----------
            obj: FileRepoObject
                the repo object for which a locator will be returned

            Returns
            -------
            FileObjectLocator
                the locator for the given repo object
            List[str]
                the path specification
        """
        return FileObjectLocator(obj.subpath(len(path_spec) + 1), path_spec)

    @staticmethod
    def from_date(date_period: DatePeriodType, the_date: Date, 
            objectname_spec: str, path_spec: List[str]) -> 'FileObjectLocator':
        """
            Get an object locator for the given date using the provided name specification

            Parameters
            ----------
            date_period: DatePeriodType
                the date period: day or quarter
            the_date: Date
                the date
            objectname_spec: str
                the object name specification
            path_spec: str
                the path specification

            Returns
            -------
            FileObjectLocator
                the locator
        """
        path: List[str] = [the_date.format(spec, date_period) for spec in path_spec]
        path.append(the_date.format(objectname_spec, date_period))    
        return FileObjectLocator(path, path_spec)

    def __len__(self) -> int:
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

            Returns
            -------
            str
                the key's element of the locator
        """
        return self.path[int(key)]

    def __iter__(self):
        """
            Iterates over the locator's path

            Returns
            -------
            Iterator
                the iterator
        """
        return iter(self.path)

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
                the date period: quarter or day
        """
        return DatePeriodType.from_string(self.get_param('t'))

    def date(self, objectname_spec: str) -> Date:
        """
            Returns the date of the locator

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
                return parse(s, self.path[i])[param_name]
            i += 1
        return None
            

class FileRepoFS(RepoFS, FileRepoDirVisitor):
    def __init__(self, dir: Path, repo_format: RepoFormat) -> None:
        self.__root : FileRepoDir = FileRepoDir(dir)
        self.__repo_format: RepoFormat = repo_format
        self.__indices: Dict[str, FileRepoObject] = {}

    def list_years(self, period_type: DatePeriodType) -> List[int]:
        """
            List years available in the repo

            Returns
            -------
            List[int]
                a list of year numbers
        """
        return [int(name) for (name, _) in self.__root[str(period_type)]]

    def get_update_list(self, from_date: Date, to_date: Date) -> List[str]:
        """
            Identifies objects that are not in the repository or need to be updated for the given dates

            Parameters
            ----------
            from_date: Date
                the start date
            to_date: Date
                the end date

            Returns
            -------
            List[str]
                a list of missing objects
        """
        used_year: int = 0
        used_quarter: int = 0
        holidays: USHoliday = None

        day_spec: str = self.__repo_format.object_specs[DatePeriodType.DAY]
        quarter_spec: str = self.__repo_format.object_specs[DatePeriodType.QUARTER]
        path_spec: List[str] = self.__repo_format.path_spec

        self.refresh()

        cur_date: Date = from_date.copy()
        updates_list: List[str] = []
        for _ in range(to_date.diff_days(from_date)):
            (cur_year, cur_quarter, _, _, _) = cur_date.parts()

            if cur_year != used_year:
                # Moving to the first or to the next year
                holidays = USHoliday(cur_year)
                used_year, used_quarter = cur_year, 0

            if not (cur_date.is_weekend() or cur_date in holidays):
                loc: str = self.locator(DatePeriodType.DAY, day_spec, path_spec, cur_date)
                if loc not in self.__indices:
                    if cur_quarter != used_quarter:
                        # Add a quartely file to the update list only if it has not been added before
                        updates_list.append(self.locator(DatePeriodType.QUARTER, quarter_spec,path_spec, cur_date))
                        used_quarter = cur_quarter
                    # Add a daily file to the update list
                    updates_list.append(loc)
            # next date
            cur_date += 1

        return updates_list

    @staticmethod
    def locator(period: DatePeriodType, objectname_spec: str, path_spec: List[str], the_date: Date) -> str:
        return str(FileObjectLocator.from_date(period, the_date, objectname_spec, path_spec))

    def get_object(self, rel_path: str) -> RepoObject:
        """
            Get a repo object at the given relative path

            Returns
            -------
            RepoObject | None
                the repo objet at the given path. If no object is found then None is returned
        """
        loc: FileObjectLocator = FileObjectLocator(rel_path, self.__repo_format.path_spec)
        e: RepoEntity = self.__root
        for i in loc:
            if i in e:
                e = e[i]
            else:
               return None
        return e

    def new_object(self, rel_path: str, object_name: str) -> RepoObject:
        """
            Creates a new object at the provided path

            Parameters
            ----------
            real_path: str
                the path to the object
            object_name: str
                the object name

            Returns
            -------
            RepoObject
                the newly created repo object
        """
        loc: FileObjectLocator = FileObjectLocator(rel_path, self.__repo_format.path_spec)
        e: RepoEntity = self.__root

        for i in range(len(loc)):
            name: str = loc[i]
            if name not in e:
                e = e.new_dir(name)
            else:
                e = e[name]
        
        return e.new_object(object_name)

    def refresh(self) -> None:
        """
            Synchronizes the FS with physical data
        """
        self.__indices.clear()
        self.__root.refresh()
        self.__root.visit(self)

    def visit(self, object: FileRepoObject) -> bool:        
        loc: FileObjectLocator = FileObjectLocator.locate(object, self.__repo_format.path_spec)
        self.__indices[str(loc)] = object
        return True
