"""
Storage base
"""
from collections import defaultdict
from typing import DefaultDict, List

from ..constants import Status


class Storage:
    """
    Store recent statuses
    """
    path: str
    data: DefaultDict[str, List[Status]]
    max_memory: int

    def __init__(self, path: str, max_memory: int = 10) -> None:
        self.path = path
        self.data = defaultdict(list)
        self.max_memory = max_memory

    def load(self) -> None:
        raise NotImplementedError()

    def save(self) -> None:
        raise NotImplementedError()

    def set(self, key: str, status: Status) -> None:
        """
        Add a status to the memory
        """
        self.data[key].append(status)

        # Assert max memory
        if len(self.data[key]) > self.max_memory:
            self.data[key] = self.data[key][self.max_memory:]

    def latest(self, key: str, count: int) -> List[Status]:
        """
        Return latest {count} statuses
        """
        return self.data[key][-count:]
