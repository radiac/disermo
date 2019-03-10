"""
Base class for all notifiers
"""
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:  # pragma: no cover
    from ..checks import Check
    from ..constants import Status
    from ..node import Node
    from ..storage import Storage, GroupedStatus


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
        generator: GroupedStatus = storage.get(key=uid, grouped=True)

        # Get first (newest) status
        first_status: Status
        first_count: int
        try:
            first_status, first_count = next(generator)
        except StopIteration:
            # Nothing on the stack
            if self.after <= 1:
                return True
            return False

        # See if this is starting or continuing a trend
        if first_status == status:
            if first_count >= self.after:
                # Continuing trend - no change
                return False

            elif first_count + 1 == self.after:
                # This next one will start a new trend
                # But what about the previous trend; is this actually a change?
                past_status: Status
                past_count: int
                for past_status, past_count in generator:
                    if past_count >= self.after:
                        # Found the previous trend
                        if past_status == status:
                            # This is returning to an old trend - no change
                            return False
                        else:
                            # This is starting a new trend
                            return True

                # Haven't found a previous trend - this is starting a new one
                return True

        else:
            # Status doesn't match, it can't be a trend...
            if self.after <= 1:
                # ... unless we start a new trend immediately
                return True

        # Have not started a new trend yet - either a new status, or not enough
        return False
