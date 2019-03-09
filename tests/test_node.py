"""
Test disermo/node.py
"""
from io import StringIO

from disermo.checks.base import Check
from disermo.constants import Status
from disermo.node import Node
from disermo.notifiers.stream import Stream
from disermo.storage.base import Storage


class MockCheck(Check):
    mock_status = Status.DISABLED

    def get_uid(self):
        return self.label

    def update(self):
        self.status = self.mock_status


class MockStorage(Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loaded = False
        self.saved = False

    def load(self) -> None:
        self.loaded = True

    def save(self) -> None:
        self.saved = True


class MockNotifier(Stream):
    def __init__(self):
        super().__init__(StringIO())


def gen_tree():
    """
    Generate following check tree:

        node
            check 0
            check 1
                check 2
            check 3
                check 4
                    check 5
    """
    check0 = MockCheck('check 0')
    check1 = MockCheck('check 1')
    check2 = MockCheck('check 2')
    check3 = MockCheck('check 3')
    check4 = MockCheck('check 4')
    check5 = MockCheck('check 5')
    node = Node('node')
    node.add(check0)
    node.add(check1)
    check1.add(check2)
    node.add(check3)
    check3.add(check4)
    check4.add(check5)
    return node, [check0, check1, check2, check3, check4, check5]


def test_node_children():
    node, checks = gen_tree()
    assert node.subchecks == [checks[0], checks[1], checks[3]]


def test_iter_flat_checks__tree_is_flattened():
    node, checks = gen_tree()
    assert list(node.iter_flat_checks()) == [node] + checks


def test_iter_flat_depth_checks__tree_is_flattened_with_depths():
    node, checks = gen_tree()
    assert list(node.iter_flat_depth_checks()) == [
        (node, 0),
        (checks[0], 1),
        (checks[1], 1),
        (checks[2], 2),
        (checks[3], 1),
        (checks[4], 2),
        (checks[5], 3),
    ]


def test_iter_flat_labelled_checks__tree_is_flattened_with_labels():
    node, checks = gen_tree()
    assert list(node.iter_flat_labelled_checks()) == [
        (node, ['node']),
        (checks[0], ['node', 'check 0']),
        (checks[1], ['node', 'check 1']),
        (checks[2], ['node', 'check 1', 'check 2']),
        (checks[3], ['node', 'check 3']),
        (checks[4], ['node', 'check 3', 'check 4']),
        (checks[5], ['node', 'check 3', 'check 4', 'check 5']),
    ]


def test_check():
    # Set up tree with notifiers on each node
    node, checks = gen_tree()
    notifierNode = MockNotifier()
    notifiers = [MockNotifier()] * 6
    node.notify(notifierNode)
    for i in range(6):
        checks[i].notify(notifiers[i])
    storage = MockStorage()

    node.check(storage)

    assert storage.data == {
        'node': [(Status.DISABLED, 1)],
        'check 0': [(Status.DISABLED, 1)],
        'check 1': [(Status.DISABLED, 1)],
        'check 2': [(Status.DISABLED, 1)],
        'check 3': [(Status.DISABLED, 1)],
        'check 4': [(Status.DISABLED, 1)],
        'check 5': [(Status.DISABLED, 1)],
    }

    notification = (
        'node: Disabled\n'
        '  check 0: Disabled\n'
        '  check 1: Disabled\n'
        '    check 2: Disabled\n'
        '  check 3: Disabled\n'
        '    check 4: Disabled\n'
        '      check 5: Disabled\n'
    )
    assert notifierNode.stream.getvalue() == notification
    for i in range(6):
        assert notifiers[i].stream.getvalue() == notification
