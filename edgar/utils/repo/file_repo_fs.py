from edgar.utils.repo.repo_fs import RepoObject, RepoFS, RepoEntity, RepoFormat, RepoDirVisitor
from edgar.utils.repo.file_repo_dir import FileRepoDir
from edgar.utils.repo.file_object_locator import FileObjectLocator as ObjLoc
from edgar.utils.date.date_utils import Date, DatePeriodType
from edgar.utils.date.holidays import us_holidays
from pathlib import Path
from typing import Dict, List


class FileRepoFS(RepoFS, RepoDirVisitor):
    def __init__(self, root: Path, format: RepoFormat) -> None:
        self.__root     : FileRepoDir = FileRepoDir(root)
        self.__format   : RepoFormat = format
        self.__index    : Dict[str, RepoObject] = {}

    def find_missing(self, from_date: Date, to_date: Date) -> List[str]:
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
        self.refresh()

        in_y, in_q = 0, 0
        h: us_holidays = None
        u: List[str] = []
        d: Date = from_date.copy()

        for _ in range(to_date.diff_days(from_date)):
            (y, q, *_) = d.parts()

            if y != in_y:
                # Moving to the first or to the next year
                h = us_holidays(y)
                in_y, in_q = y, 0

            if not (d.is_weekend() or d in h):
                o: str = str(self.__ref(DatePeriodType.DAY, d))
                if o not in self.__index:
                    if q != in_q:
                        # Add a quartely file to the update list only if it has not been added before
                        u.append(str(self.__ref(DatePeriodType.QUARTER, d)))
                        in_q = q

                    # Add a daily file to the update list
                    u.append(o)
            # next date
            d += 1

        return u

    def __ref(self, date_period: DatePeriodType, the_date: Date) -> ObjLoc:
        return ObjLoc.from_date(date_period, the_date, 
            self.__format.name_spec[date_period],  
            self.__format.path_spec)

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
        loc: ObjLoc = ObjLoc(obj_uri, self.__format.path_spec)
        e: RepoEntity = self.__root
        for i in loc:
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
        loc: ObjLoc = ObjLoc(obj_path, self.__format.path_spec)
        e: RepoEntity = self.__root

        for i in range(len(loc)):
            name: str = loc[i]
            if name not in e:
                e = e.new_dir(name)
            else:
                e = e[name]
        
        return e.new_object(obj_name)

    def find(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:
        """
            Finds an object for the given date and period type

            Parameters
            ----------
            date_period: DatePeriodType
                the date period type            
            the_date: Date
                the date

            Returns
            -------
            RepoObject
                the object
        """
        return self.get_object(str(self.__ref(date_period, the_date)))

    def create(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:
        """
            Creates an object for the given date and period type

            Parameters
            ----------
            date_period: DatePeriodType
                the period type
            the_date: Date
                the date

            Returns
            -------
            RepoObject
            
        """
        p: ObjLoc = self.__ref(date_period, the_date)
        return self.new_object(p.parent(), p[-1])

    def refresh(self) -> None:
        """
            Synchronizes the FS with physical data
        """
        self.__index.clear()
        self.__root.refresh()
        self.__root.visit(self)

    def visit(self, obj: RepoObject) -> bool:
        loc: ObjLoc = ObjLoc.locate(obj, self.__format.path_spec)
        self.__index[str(loc)] = obj
        return True
