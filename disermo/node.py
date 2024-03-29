"""
Node object
"""
from collections import defaultdict
from typing import List, DefaultDict, Iterator, Tuple

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
        checks: List[Check] = list(self.iter_flat_checks())

        # Collect notifiers
        notifiers: DefaultDict[Notifier, List[Check]] = defaultdict(list)
        for check in checks:
            for notifier in check.notifiers:
                notifiers[notifier].append(check)

        # Load storage so notifiers understand status context
        storage.load()

        # Call notifiers
        for notifier, notifier_checks in notifiers.items():
            notifier.process(self, storage, notifier_checks)

        # Store statuses for trend spotting
        for check in checks:
            storage.set(check.uid, check.status)
        storage.save()

        return status

    def iter_flat_checks(self) -> Iterator[Check]:
        """
        Generator to return a flat list of the node tree, starting with self
        """
        checks: List[Check] = [self]
        while checks:
            check = checks.pop(0)
            checks = check.subchecks + checks
            yield check

    def iter_flat_depth_checks(self) -> Iterator[Tuple[Check, int]]:
        """
        Generator to return a flat list of (check, depth) pairs of the node
        tree, starting with self, where depth is a 0-indexed depth (0 is self)
        """
        checks: List[Tuple[Check, int]] = [(self, 0)]
        while checks:
            check, depth = checks.pop(0)
            checks = [
                (subcheck, depth + 1)
                for subcheck in check.subchecks
            ] + checks
            yield (check, depth)

    def iter_flat_labelled_checks(self) -> Iterator[Tuple[Check, List[str]]]:
        """
        Generator to return a flat list of (check, labels) pairs of the node
        tree, starting with self, where ``labels`` is a list of all parent
        labels, in order oldest first
        """
        checks: List[Tuple[Check, List[str]]] = [(self, [self.label])]
        while checks:
            # Look at next and search its children
            check, label = checks.pop(0)
            checks = [
                (subcheck, label + [subcheck.label])
                for subcheck in check.subchecks
            ] + checks

            # See if we've found one
            yield (check, label)
