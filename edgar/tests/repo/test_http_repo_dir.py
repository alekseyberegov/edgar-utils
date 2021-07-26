from edgar.utils.repo.http_repo_object import HttpRepoObject
import unittest
from unittest.mock import Mock, patch, call
from edgar.utils.repo.http_repo_dir import HttpRepoDir


class TestHttpRepoDir(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = HttpRepoDir('http://www.site.com/a/b/c/')
        return super().setUp()

    def tearDown(self) -> None:
        del self.dir
        return super().tearDown()

    def test_as_uri(self) -> None:
       assert self.dir.as_uri() == 'http://www.site.com/a/b/c/'

    @patch('requests.head', return_value=Mock(status_code=200, **{'iter_content.return_value':[]}))
    def test_exists(self, mock_head):
        assert self.dir.exists()

    @patch('requests.head', return_value=Mock(status_code=400, **{'iter_content.return_value':[]}))
    def test_not_exists(self, mock_head):
        assert not self.dir.exists()

    def test_subpath(self):
        assert self.dir.subpath(1) == ['c']
        assert self.dir.subpath(2) == ['b', 'c']
        assert self.dir.subpath(3) == ['a', 'b', 'c']

    def test_new_dir(self):
        child: HttpRepoDir = self.dir.new_dir('d')
        assert child.as_uri() == 'http://www.site.com/a/b/c/d/'

    def test_new_object(self):
        child: HttpRepoObject = self.dir.new_object("master.idx")
        assert child.as_uri() == 'http://www.site.com/a/b/c/master.idx'