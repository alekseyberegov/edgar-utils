import unittest
from unittest.mock import MagicMock, patch, call
from edgar.utils.repo.http_repo_object import HttpRepoObject
from edgar.tests.mock import MockResponse
from typing import Iterator

class TestHttpRepoObject(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = MagicMock()
        self.dir.as_uri.return_value = 'http://www.site.com/a/'
        return super().setUp()

    def tearDown(self) -> None:
        del self.dir
        return super().tearDown()

    def test_as_uri(self):
        obj = HttpRepoObject(self.dir, 'master.idx')
        assert self.dir.__setitem__.call_args_list == [call('master.idx', obj)]
        assert obj.as_uri() == 'http://www.site.com/a/master.idx'

    @patch('requests.get', return_value=MockResponse(['hello'], 200))
    def test_inp_one_chunk(self, mock_get):
        obj = HttpRepoObject(self.dir, 'master.idx')
        it: Iterator = obj.inp()
        assert next(it) == 'hello'

    @patch('requests.get', return_value=MockResponse(['hello', 'world'], 200))
    def test_inp_two_chunks(self, mock_get):
        obj = HttpRepoObject(self.dir, 'master.idx')
        it: Iterator = obj.inp()
        assert next(it) == 'hello'
        assert next(it) == 'world'

    @patch('requests.get', return_value=MockResponse([], 400))
    def test_inp_failed(self, mock_get):
        obj = HttpRepoObject(self.dir, 'master.idx')
        it: Iterator = obj.inp()
        assert next(it, None) is None
 
    @patch('requests.head', return_value=MockResponse([], 200))
    def test_exists(self, mock_head):
        obj = HttpRepoObject(self.dir, 'master.idx')
        assert obj.exists()

    @patch('requests.head', return_value=MockResponse([], 400))
    def test_not_exists(self, mock_head):
        obj = HttpRepoObject(self.dir, 'master.idx')
        assert not obj.exists()

    def test_subpath(self):
        obj = HttpRepoObject(self.dir, 'master.idx')
        assert obj.subpath(1) == ['master.idx']
        assert obj.subpath(2) == ['a', 'master.idx']

