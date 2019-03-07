"""
Storage base
"""
from collections import defaultdict
from typing import DefaultDict, List, Tuple, Iterator, overload
from typing_extensions import Literal

from ..constants import Status


GroupedStatus = Iterator[Tuple[Status, int]]
FlatStatus = Iterator[Status]


class Storage:
    """
    Store recent statuses
    """
    path: str
    data: DefaultDict[str, List[Tuple[Status, int]]]
    max_memory: int

    def __init__(self, max_memory: int = 10) -> None:
        self.data = defaultdict(list)
        self.max_memory = max_memory

    def load(self) -> None:
        raise NotImplementedError()  # pragma: no cover

    def save(self) -> None:
        raise NotImplementedError()  # pragma: no cover

    def set(self, key: str, status: Status) -> None:
        """
        Add a status to the memory
        """
        count = 1
        if self.data[key]:
            last_status: Status
            last_count: int
            last_status, last_count = self.data[key][-1]
            if last_status == status:
                # Increment the last status rather than creating a new one
                self.data[key].pop()
                count = last_count + 1

        self.data[key].append((status, count))

        # Assert max memory
        if len(self.data[key]) > self.max_memory:
            self.data[key] = self.data[key][-self.max_memory:]

    @overload
    def get(self, key: str, grouped: Literal[False]) -> FlatStatus:
        pass  # pragma: no cover

    @overload  # noqa: F811 until flake8 supports PEP 484
    def get(self, key: str, grouped: Literal[True]) -> GroupedStatus:
        pass  # pragma: no cover

    def get(self, key, grouped=False):  # noqa: E501,F811 until flake8 supports PEP 484
        """
        Generator to return stored statuses, with most recent first
        """
        status: Status
        count: int
        for status, count in reversed(self.data[key]):
            if grouped:
                yield status, count
            else:
                for i in range(count):
                    yield status
