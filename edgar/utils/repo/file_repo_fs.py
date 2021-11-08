"""
    File-based document repository
"""
from typing import Dict, List, Iterator
from pathlib import Path
from edgar.utils.repo.repo_fs import RepoObject, RepoFS, RepoEntity, RepoDirVisitor, RepoURI
from edgar.utils.repo.repo_format import RepoObjectPath, RepoFormat
from edgar.utils.repo.file_repo_dir import FileRepoDir
from edgar.utils.date.date_utils import Date, DatePeriodType
from edgar.utils.date.holidays import us_holidays


class FileRepoFS(RepoFS, RepoDirVisitor):
    """
        The class represents a file-based repository
    """
    def __init__(self, root: Path, repo_format: RepoFormat) -> None:
        self.__root     : FileRepoDir = FileRepoDir(root)
        self.__format   : RepoFormat = repo_format
        self.__index    : Dict[str, RepoObject] = {}

    def find_missing(self, from_date: Date, to_date: Date) -> List[str]:
        miss_list: List[str] = []
        for repo_uri in self.iterate_missing(from_date, to_date):
            miss_list.append(str(repo_uri))
        return miss_list

    def iterate_missing(self, from_date: Date, to_date: Date) -> Iterator[RepoURI]:
        """
            Identifies objects that are not in the repository
            or need to be updated for the given dates

            Parameters
            ----------
            from_date: Date
                the start date
            to_date: Date
                the end date

            Returns
            -------
            Iterator[str]
                an iterator for missing objects
        """
        self.refresh()

        track_year, track_quarter = 0, 0
        cur_holidays: us_holidays = None
        cur_date: Date = from_date.copy()

        for _ in range(to_date.diff_days(from_date)):
            (cur_year, cur_quarter, *_) = cur_date.tuple()

            if cur_year != track_year:
                # Moving to the first or to the next year
                cur_holidays = us_holidays(cur_year)
                track_year, track_quarter = cur_year, 0

            if not (cur_date.is_weekend() or cur_date in cur_holidays):
                obj_path: RepoObjectPath = RepoObjectPath.from_date(
                    DatePeriodType.DAY, cur_date, self.__format)
                if str(obj_path) not in self.__index:
                    if cur_quarter != track_quarter:
                        # Add a quartely file to the update list
                        # only if it has not been added before
                        yield RepoObjectPath.from_date(
                            DatePeriodType.QUARTER, cur_date, self.__format)
                        track_quarter = cur_quarter

                    # Add a daily file to the update list
                    yield obj_path
            # next date
            cur_date += 1

    def get_object(self, obj_uri: str) -> RepoObject:
        """
            Get a repo object at the given relative path

            Parameters
            ----------
            obj_uri: str
                the object URI

            Returns
            -------
            RepoObject | None
                the repo objet at the given path. If no object is found then None is returned
        """
        obj_path: RepoObjectPath = RepoObjectPath.from_uri(obj_uri, self.__format)
        cur_ent: RepoEntity = self.__root
        for i in obj_path:
            if i in cur_ent:
                cur_ent = cur_ent[i]
            else:
                return None
        return cur_ent

    def new_object(self, obj_path: str, obj_name: str) -> RepoObject:
        """
            Creates a new object at the provided path

            Parameters
            ----------
            obj_path: str
                the path to the object
            obj_name: str
                the object name

            Returns
            -------
            RepoObject
                the newly created repo object
        """
        obj_path: RepoObjectPath = RepoObjectPath.from_uri(obj_path, self.__format)
        cur_dir: RepoEntity = self.__root

        for name in obj_path:
            if name not in cur_dir:
                cur_dir = cur_dir.new_dir(name)
            else:
                cur_dir = cur_dir[name]

        return cur_dir.new_object(obj_name)

    def find(self, period_type: DatePeriodType, the_date: Date) -> RepoObject:
        """
            Finds an object for the given date and period type

            Parameters
            ----------
            period_type: DatePeriodType
                the date period type
            the_date: Date
                the date

            Returns
            -------
            RepoObject
                the object
        """
        return self.get_object(str(RepoObjectPath.from_date(period_type, the_date, self.__format)))

    def create(self, period_type: DatePeriodType, the_date: Date) -> RepoObject:
        """
            Creates an object for the given date and period type

            Parameters
            ----------
            period_type: DatePeriodType
                the period type
            the_date: Date
                the date

            Returns
            -------
            RepoObject

        """
        obj_path: RepoObjectPath = RepoObjectPath.from_date(period_type, the_date, self.__format)
        return self.new_object(obj_path.parent(), obj_path[-1])

    def refresh(self) -> None:
        """
            Synchronizes the FS with physical data
        """
        self.__index.clear()
        self.__root.refresh()
        self.__root.visit(self)

    def visit(self, obj: RepoObject) -> bool:
        obj_path: RepoObjectPath = RepoObjectPath.from_object(obj, self.__format)
        self.__index[str(obj_path)] = obj
        return True
