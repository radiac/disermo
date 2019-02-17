"""
Node object
"""
from collections import defaultdict
from typing import List, DefaultDict

from .checks.base import Check
from .constants import Status
from .notifiers import Notifier
from .storage import Storage


class Node(Check):
    def check(self, storage: Storage) -> Status:
        """
        Run the checks and notify
        """
        status: Status = super().run()

        # Collect flat list of all checks
        checks: List[Check] = list(self.get_flat_checks())

        # Collect notifiers
        notifiers: DefaultDict[Notifier, List[Check]] = defaultdict(list)
        for check in checks:
            for notifier in check.notifiers:
                notifiers[notifier].append(check)

        # Load storage so notifiers understand status context
        storage.load()

        # Call notifiers
        for notifier, checks in notifiers.items():
            notifier.process(self, storage, checks)

        # Store statuses for trend spotting
        for check in checks:
            storage.set(check.uid, check.status)
        storage.save()

        return status

    def get_flat_checks(self):
        """
        Generator to return a flat list of nested subchecks
        """
        checks: List[Check] = self.subchecks[:]
        while checks:
            check = checks.pop()
            checks.extend(check.subchecks)
            yield check
