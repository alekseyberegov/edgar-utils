import unittest
from unittest import mock
from typing import Dict
from edgar.utils.repo.http_client import HttpClient

    
class TestHttpClient(unittest.TestCase):
    route_map: Dict[str, mock.Mock] = {
        'http://test.com/a/b/c'         : mock.Mock(status_code=200, **{'iter_content.return_value':(['abc'])}),
        'http://test.com/a/b/c/file.idx': mock.Mock(status_code=200, **{'iter_content.return_value':(['123'])})
    }

    @mock.patch('requests.get')
    def test_inp_basedir_success(self, mock_get):
        mock_get.side_effect = self.mock_http_get
        http_client: HttpClient = HttpClient('http://test.com/a/')
        status_code = http_client.get('b/c')
        assert status_code == 200
        content = next(http_client.inp())
        assert content == 'abc'
        
    @mock.patch('requests.get')
    def test_inp_url_success(self, mock_get):
        mock_get.side_effect = self.mock_http_get
        http_client: HttpClient = HttpClient()
        status_code = http_client.get('http://test.com/a/b/c')
        assert status_code == 200
        content = next(http_client.inp())
        assert content == 'abc'

    @mock.patch('requests.get')
    def test_inp_file_success(self, mock_get):
        mock_get.side_effect = self.mock_http_get
        http_client: HttpClient = HttpClient('http://test.com/a/')
        status_code = http_client.get('b/c/file.idx')
        assert status_code == 200
        content = next(http_client.inp())
        assert content == '123'
    
    @mock.patch('requests.get')
    def test_inp_file_failure(self, mock_get):
        mock_get.side_effect = self.mock_http_get
        http_client: HttpClient = HttpClient('http://test.com/x/')
        status_code = http_client.get('b/c/file.idx')
        assert status_code == 404

    def mock_http_get(self, *args, **kwargs):
        return self.route_map[args[0]] if args[0] in self.route_map else mock.Mock(status_code=404)