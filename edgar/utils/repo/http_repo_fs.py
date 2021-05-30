from edgar.utils.repo.repo_fs import RepoFS, RepoObject, RepoFormatter
from edgar.utils.repo.http_repo_dir import HttpRepoDir
from edgar.utils.repo.http_repo_object import HttpRepoObject
from edgar.utils.date.date_utils import DatePeriodType, Date
from edgar.utils.repo.http_tools import make_url
from typing import List

class HttpRepoFS(RepoFS):
    def __init__(self, base_url: str, formatter: RepoFormatter) -> None:
        self.__formatter = formatter
        self.__root = HttpRepoDir(base_url)

    def find_missing(self, from_date: Date, to_date: Date) -> List[str]:
        return []

    def find(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:
        path: List[str] = self.__formatter.format(date_period, the_date)
        dir: HttpRepoDir = self.__root
        for i in path[:-1]:
            dir = HttpRepoDir(make_url(dir.as_uri(), i), dir)
        return HttpRepoObject(dir, path[-1])

    def create(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:
        return self.find(date_period, the_date)

    def refresh(self) -> None:
        pass