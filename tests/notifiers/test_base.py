"""
Test disermo/notifiers/base.py
"""
from typing import List, Union

from disermo.checks.base import Check
from disermo.constants import Status
from disermo.node import Node
from disermo.notifiers.base import Notifier, TrendNotifier
from disermo.storage.base import Storage


class MockNotifier(Notifier):
    sent: Union[List[Check]]

    def __init__(self):
        self.sent = None
        super().__init__()

    def send(self, node: Node, checks: List[Check]) -> None:
        self.sent = checks


def test_check_disabled():
    # Other tests assume this
    assert Check().status == Status.DISABLED


def test_notifier_process__sends_check():
    notifier = MockNotifier()
    storage = Storage()
    check1 = Check()
    check2 = Check()
    node = Node()
    assert notifier.sent is None
    assert notifier.test(storage, check1) is True

    notifier.process(node=node, storage=storage, checks=[check1, check2])

    assert notifier.sent == [check1, check2]


def test_trendnotifier_process__not_enough_to_find_trend__test_fails():
    notifier = TrendNotifier(after=5)
    storage = Storage()
    check = Check()
    assert notifier.test(storage, check) is False


def test_trendnotifier_process__continues_trend__test_fails():
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [(Status.DISABLED, 3)]
    check = Check()
    assert notifier.test(storage, check) is False


def test_trendnotifier_process__continues_large_trend__test_fails():
    """
    Same as test_trendnotifier_process__continues_trend__test_fails
    just testing bounds
    """
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [(Status.DISABLED, 30)]
    check = Check()
    assert notifier.test(storage, check) is False


def test_trendnotifier_process__no_stack_new_trend_after_one__test_passes():
    notifier = TrendNotifier(after=1)
    storage = Storage()
    storage.data['check'] = []
    check = Check()
    assert notifier.test(storage, check) is True


def test_trendnotifier_process__new_trend_after_one__test_passes():
    notifier = TrendNotifier(after=1)
    storage = Storage()
    storage.data['check'] = [(Status.OK, 1)]
    check = Check()
    assert notifier.test(storage, check) is True


def test_trendnotifier_process__new_trend_after_more__test_passes():
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [
        (Status.OK, 1), (Status.DISABLED, 2),
    ]
    check = Check()
    assert notifier.test(storage, check) is True


def test_trendnotifier_process__flipping_value__test_fails():
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [
        (Status.OK, 1), (Status.DISABLED, 1), (Status.OK, 1),
    ]
    check = Check()
    assert notifier.test(storage, check) is False


def test_trendnotifier_process__single_value_oldest__test_passes():
    """
    The oldest check was a flipped value which didn't form a trend, but the
    new one does - new trend
    """
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [
        (Status.DISABLED, 1), (Status.OK, 1), (Status.DISABLED, 2),
    ]
    check = Check()
    assert notifier.test(storage, check) is True


def test_trendnotifier_process__old_trend__test_fails():
    """
    The oldest check was a flipped value which did form a trend; the new one
    is effectively a continuation of the old trend and should not trigger.
    """
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [
        (Status.DISABLED, 3), (Status.OK, 1), (Status.DISABLED, 2),
    ]
    check = Check()
    assert notifier.test(storage, check) is False


def test_trendnotifier_process__old_large_trend__test_fails():
    """
    Same as test_trendnotifier_process__old_trend__test_fails, just checking
    bounds
    """
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [
        (Status.DISABLED, 30), (Status.OK, 1), (Status.DISABLED, 2),
    ]
    check = Check()
    assert notifier.test(storage, check) is False


def test_trendnotifier_process__flip_but_old_trend_different__test_passes():
    """
    There is an old trend which was flipped to a new state which was too short
    to trigger a new trend, but this new trend does not match the old one - so
    should be detected as a new trend
    """
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [
        (Status.ERROR, 3), (Status.OK, 1), (Status.DISABLED, 2),
    ]
    check = Check()
    assert notifier.test(storage, check) is True
