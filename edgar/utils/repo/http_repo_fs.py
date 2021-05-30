from edgar.utils.repo.repo_fs import RepoFS, RepoObject, RepoFormat
from edgar.utils.date.date_utils import DatePeriodType, Date
from typing import List

class HttpRepoFS(RepoFS):
    def __init__(self, base_url: str, format: RepoFormat) -> None:
        self.__base_url = base_url
        self.__format = format

    def find_missing(self, from_date: Date, to_date: Date) -> List[str]:
        pass

    def find(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:        
        pass

    def create(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:
        pass

    def refresh(self) -> None:
        pass