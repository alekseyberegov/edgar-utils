from urllib.parse import urljoin
from edgar.utils.date.date_utils import DatePeriodType

def make_url(base: str, url: str) -> str:
    return urljoin(base, url)

def norm_dir_url(url: str) -> str:
    return url.rstrip("/") + "/"

def new_dir_url(base: str, url: str) -> str:
    return make_url(base, url.rstrip("/"))  + "/"

def get_index_macro() -> callable:
    return lambda period_type, date: 'daily-index' if period_type == DatePeriodType.DAY else 'full-index'