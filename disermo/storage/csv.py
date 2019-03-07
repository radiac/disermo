"""
CSV storage
"""
import csv
import os

from ..constants import Status
from .base import Storage


class CSV(Storage):
    """
    Store records in CSV format:

        key,status|count,status|count,...

    with oldest status first
    """
    SEPARATOR = '|'

    def __init__(self, path: str, max_memory: int = 10) -> None:
        super().__init__(max_memory=max_memory)
        self.path = path

    def load(self) -> None:
        if not os.path.exists(self.path):
            return

        with open(self.path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.data[row[0]] = [
                    (Status(int(status)), int(count))
                    for (status, count) in [
                        cell.split(self.SEPARATOR, 1)
                        for cell in row[1:]
                    ]
                ]

    def save(self) -> None:
        with open(self.path, 'w') as file:
            writer = csv.writer(file)
            for key, values in self.data.items():
                writer.writerow([key] + [
                    f'{status.value}{self.SEPARATOR}{count}'
                    for status, count in values
                ])
