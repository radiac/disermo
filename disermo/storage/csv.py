"""
CSV storage
"""
import csv

from ..constants import Status
from .base import Storage


class CSV(Storage):
    def load(self) -> None:
        with open(self.path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.data[row[0]] = [Status(value) for value in row[1:]]

    def save(self) -> None:
        with open(self.path, 'w') as file:
            writer = csv.writer(file)
            for key, statuses in self.data.items():
                writer.writerow([key] + [status.value for status in statuses])
