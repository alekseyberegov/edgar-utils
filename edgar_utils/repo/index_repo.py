from pathlib import Path

class IndexRepo(object):
    def __init__(self, base_dir: str) -> None:
        self.base = Path(base_dir)