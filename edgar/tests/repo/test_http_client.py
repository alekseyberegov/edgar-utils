import unittest
from unittest import mock
from typing import Dict
from edgar.utils.repo.http_client import HttpClient

class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def iter_content(self, chuck_size):
        return iter([self.content])

route_map: Dict[str, MockResponse] = {
    'http://test.com/a/b/c'         : MockResponse('abc', 200),
    'http://test.com/a/b/c/file.idx': MockResponse('123', 200)
}

def mocked_requests_get(*args, **kwargs):
    print(args[0])
    if args[0] in route_map:
        return route_map[args[0]]
    return MockResponse(None, 404)

class TestHttpClient(unittest.TestCase):
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_inp_basedir_success(self, mock_get):
        http_client: HttpClient = HttpClient('http://test.com/a/')
        status_code = http_client.get('b/c')
        assert status_code == 200
        content = next(http_client.inp())
        assert content == 'abc'
        
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_inp_url_success(self, mock_get):
        http_client: HttpClient = HttpClient()
        status_code = http_client.get('http://test.com/a/b/c')
        assert status_code == 200
        content = next(http_client.inp())
        assert content == 'abc'

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_inp_file_success(self, mock_get):
        http_client: HttpClient = HttpClient('http://test.com/a/')
        status_code = http_client.get('b/c/file.idx')
        assert status_code == 200
        content = next(http_client.inp())
        assert content == '123'
    
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_inp_file_failure(self, mock_get):
        http_client: HttpClient = HttpClient('http://test.com/x/')
        status_code = http_client.get('b/c/file.idx')
        assert status_code == 404
