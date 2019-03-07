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
        if label is None:
            label = self.default_label
        self.label = label
        self.uid = self.get_uid()
        self.subchecks = []
        self.notifiers = []

        self.status = Status.DISABLED
        self.data = {}

    def __repr__(self):
        return f'<{type(self).__name__}: {self.uid}>'

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
        """
        Run the check of this node, and of all its subchecks

        The resulting status is the worst status for this node and all subnodes
        """
        self.update()
        worst: Status = self.status
        for check in self.subchecks:
            result: Status = check.run()
            if result > worst:
                worst = result

        # The status of this node is the worst found
        self.status = worst
        return worst

    def update(self) -> None:
        self.status = Status.DISABLED
        self.data = {}

    def notify(self: T, *notifiers: Notifier) -> T:
        self.notifiers.extend(notifiers)
        return self
