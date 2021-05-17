
class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def iter_content(self, chuck_size):
        return iter(self.content)