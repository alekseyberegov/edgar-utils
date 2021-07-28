from typing import List
from collections import deque

class CallTracker:
    def __init__(self) -> None:
        self.__expected = deque()

    def add_expected(self, name: str, args: List) -> None:
        self.__expected.append((name, args))

    def assertCalls(self, calls) -> None:
        for c in calls:
            e = self.__expected.popleft()
            assert c[0] == e[0]

            for i, a in enumerate(c[1]):
                assert a == e[1][i], "{0} is not equal to {1}".format(a, e[1][i])

