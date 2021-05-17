from pathlib import Path
from typing import Dict, Iterator
from urllib.parse import urljoin
import requests

def static_init(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls

@static_init
class HttpClient(object):
    http_headers: Dict[str,str] = {}

    def __init__(self, base_url: str = "") -> None:
        self.__base_url = base_url
        self.__response = None
        super().__init__()

    @classmethod
    def static_init(cls):
        headers = getattr(cls, 'http_headers')
        filename = Path(__file__).parent / 'properties' / 'http.properties'
        with open(filename, "rt") as f:
            for line in f:
                prop = line.strip()
                if prop and not prop.startswith('#'):
                    a = prop.split('=')
                    headers[a[0].strip()] = '='.join(a[1:]).strip().strip('"') 

    def get(self, loc: str) -> int:
        url = urljoin(self.__base_url, loc)
        self.__response = requests.get(url, headers=HttpClient.http_headers, stream=True)
        return self.__response.status_code

    def head(self, loc: str) -> int:
        url = urljoin(self.__base_url, loc)
        self.__response = requests.head(url, headers=HttpClient.http_headers)
        return self.__response.status_code

    def inp(self, bufsize: int = 2048) -> Iterator:
        for chunk in self.__response.iter_content(bufsize):
            yield chunk

        self.close()

    def close(self) -> None:
        if self.__response is not None:
            self.__response.close()
            self.__response = None