"""
Checks
"""
from __future__ import annotations
from typing import List, Dict, Any, TypeVar

from ..constants import Status
from ..notifiers import Notifier
from ..utils import camel_to_sentence


T = TypeVar('T', bound='Check')


class Check:
    uid: str
    label: str
    subchecks: List[Check]
    notifiers: List[Notifier]
    status: Status
    data: Dict[str, Any]

    def __init__(self, label: str = None) -> None:
        self.uid = self.get_uid()

        if label is None:
            label = self.default_label
        self.label = label
        self.subchecks = []
        self.notifiers = []

        self.status = Status.DISABLED
        self.data = {}

    @property
    def class_id(self) -> str:
        """
        Default the class ID to the class name, but expect subclasses to
        override with a string
        """
        return type(self).__name__.lower()

    @property
    def default_label(self) -> str:
        """
        Default the label to the class name, but expect subclasses to override
        with a string
        """
        return camel_to_sentence(type(self).__name__)

    def get_uid(self) -> str:
        return f'{self.class_id}'

    def add(self: T, *subchecks) -> T:
        self.subchecks.extend(subchecks)
        return self

    def run(self) -> Status:
        self.update()
        worst: Status = self.status
        for check in self.subchecks:
            result: Status = check.run()
            if result > worst:
                worst = result
        return worst

    def update(self) -> None:
        self.status = Status.DISABLED
        self.data = {}

    def notify(self: T, *notifiers: Notifier) -> T:
        self.notifiers.extend(notifiers)
        return self