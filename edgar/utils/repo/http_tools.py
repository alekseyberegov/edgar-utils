from urllib.parse import urljoin

def make_url(base: str, url: str) -> str:
    return urljoin(base, url)