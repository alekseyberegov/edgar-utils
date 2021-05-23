from urllib.parse import urljoin

def make_url(base: str, url: str) -> str:
    return urljoin(base, url)

def norm_dir_url(url: str) -> str:
    return url.rstrip("/") + "/"

def new_dir_url(base: str, url: str) -> str:
    return make_url(base, url.rstrip("/"))  + "/"