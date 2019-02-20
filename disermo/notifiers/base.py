"""
Base class for all notifiers
"""
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:  # pragma: no cover
    from ..checks import Check
    from ..constants import Status
    from ..node import Node
    from ..storage import Storage


DEFAULT_TREND_LIMIT = 5


class Notifier:
    def process(
        self,
        node: 'Node',
        storage: 'Storage',
        checks: 'List[Check]',
    ) -> None:
        """
        Process a set of checks

        Filters the checks and passes notifiable ones on to send()
        """
        # Get list of checks with something worth notifying
        notifiable = [
            check for check in checks
            if self.test(storage, check)
        ]

        # Send the notification(s) out
        self.send(node, notifiable)

    def test(self, storage: 'Storage', check: 'Check') -> bool:
        """
        Subclasses will perform tests to see if notification is required.

        This base class will just pass all notifications through
        """
        return True

    def send(self, node: 'Node', checks: 'List[Check]') -> None:
        raise NotImplementedError()  # pragma: no cover


class TrendNotifier(Notifier):
    after: int

    def __init__(self, after: int = DEFAULT_TREND_LIMIT):
        self.after = after

    def test(self, storage: 'Storage', check: 'Check') -> bool:
        """
        Performs any tests to see if the notification is required.

        Looking for a change which occurred {self.after} ago
        """
        uid: str = check.uid
        status: Status = check.status

        # Check the latest statuses to look for a trend
        latest = storage.latest(uid, self.after)
        if len(latest) < self.after:
            # Not enough to spot a trend
            return False

        # If the first matches now, no trend
        if latest[0] == status:
            return False

        # If first doesn't match and trend is 1, found new trend
        if len(latest) == 1:
            return True

        # However, if first doesn't match but the others do, found new trend
        others = list(set(latest[1:]))
        if len(others) == 1 and others[0] == status:
            return True

        # No new trend
        return False
