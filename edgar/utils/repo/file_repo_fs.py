from typing import Dict, List, Iterator
from pathlib import Path
from edgar.utils.repo.repo_fs import RepoObject, RepoFS, RepoEntity, RepoDirVisitor, RepoURI
from edgar.utils.repo.repo_format import RepoObjectPath, RepoFormat
from edgar.utils.repo.file_repo_dir import FileRepoDir
from edgar.utils.date.date_utils import Date, DatePeriodType
from edgar.utils.date.holidays import us_holidays


class FileRepoFS(RepoFS, RepoDirVisitor):
    def __init__(self, root: Path, repo_format: RepoFormat) -> None:
        self.__root     : FileRepoDir = FileRepoDir(root)
        self.__format   : RepoFormat = repo_format
        self.__index    : Dict[str, RepoObject] = {}

    def find_missing(self, from_date: Date, to_date: Date) -> List[str]:
        u: List[str] = []
        for o in self.iterate_missing(from_date, to_date):
            u.append(str(o))
        return u

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

        in_y, in_q = 0, 0
        h: us_holidays = None
        d: Date = from_date.copy()

        for _ in range(to_date.diff_days(from_date)):
            (y, q, *_) = d.tuple()

            if y != in_y:
                # Moving to the first or to the next year
                h = us_holidays(y)
                in_y, in_q = y, 0

            if not (d.is_weekend() or d in h):
                o: RepoObjectPath = RepoObjectPath.from_date(DatePeriodType.DAY, d, self.__format)
                if str(o) not in self.__index:
                    if q != in_q:
                        # Add a quartely file to the update list
                        # only if it has not been added before
                        yield RepoObjectPath.from_date(DatePeriodType.QUARTER, d, self.__format)
                        in_q = q

                    # Add a daily file to the update list
                    yield o
            # next date
            d += 1

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
        p: RepoObjectPath = RepoObjectPath.from_uri(obj_uri, self.__format)
        e: RepoEntity = self.__root
        for i in p:
            if i in e:
                e = e[i]
            else:
                return None
        return e

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
        p: RepoObjectPath = RepoObjectPath.from_uri(obj_path, self.__format)
        e: RepoEntity = self.__root

        for name in p:
            if name not in e:
                e = e.new_dir(name)
            else:
                e = e[name]

        return e.new_object(obj_name)

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
        p: RepoObjectPath = RepoObjectPath.from_date(period_type, the_date, self.__format)
        return self.new_object(p.parent(), p[-1])

    def refresh(self) -> None:
        """
            Synchronizes the FS with physical data
        """
        self.__index.clear()
        self.__root.refresh()
        self.__root.visit(self)

    def visit(self, obj: RepoObject) -> bool:
        p: RepoObjectPath = RepoObjectPath.from_object(obj, self.__format)
        self.__index[str(p)] = obj
        return True
