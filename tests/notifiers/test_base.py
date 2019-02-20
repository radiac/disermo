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


def test_trendnotifier_process__oldest_matches__test_fails():
    notifier = TrendNotifier(after=1)
    storage = Storage()
    storage.data['check'] = [Status.DISABLED]
    check = Check()
    assert notifier.test(storage, check) is False


def test_trendnotifier_process__new_trend_after_one__test_passes():
    notifier = TrendNotifier(after=1)
    storage = Storage()
    storage.data['check'] = [Status.OK]
    check = Check()
    assert notifier.test(storage, check) is True


def test_trendnotifier_process__new_trend_after_more__test_passes():
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [Status.OK, Status.DISABLED, Status.DISABLED]
    check = Check()
    assert notifier.test(storage, check) is True


def test_trendnotifier_process__flipping_value__test_fails():
    notifier = TrendNotifier(after=3)
    storage = Storage()
    storage.data['check'] = [Status.OK, Status.DISABLED, Status.OK]
    check = Check()
    assert notifier.test(storage, check) is False
