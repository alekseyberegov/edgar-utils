from pathlib import Path
from typing import Dict

def static_init(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls

@static_init
class HttpClient(object):
    http_headers: Dict[str,str] = {}

    @classmethod
    def static_init(cls):
        filename = Path(__file__).parent / 'properties' / 'http.properties'
        with open(filename, "rt") as f:
            for line in f:
                prop = line.strip()
                if prop and not prop.startswith('#'):
                    a = prop.split('=')
                    HttpClient.http_headers[a[0].strip()] = '='.join(a[1:]).strip().strip('"') 
