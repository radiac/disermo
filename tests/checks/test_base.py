"""
Test disermo/checks/base.py
"""
from disermo.constants import Status
from disermo.checks.base import Check
from disermo.notifiers import Notifier


class MockCheck(Check):
    def __init__(self, done_status: Status = Status.OK):
        self.done_status = done_status
        super().__init__()

    def update(self):
        self.status = self.done_status
        self.data = {'test': 'passed'}


class MockNotifier(Notifier):
    processed = False
    tested = False
    sent = False

    def process(self, *args, **kwargs):
        self.processed = True

    def test(self, *args, **kwargs):
        self.tested = True
        return False

    def send(self, *args, **kwargs):
        self.sent = True


class TestInit:
    def test_uid(self):
        check = Check()
        assert check.uid == 'check'

    def test_repr(self):
        check = Check()
        assert repr(check) == '<Check: check>'

    def test_default_label(self):
        check = Check()
        assert check.default_label == 'Check'

    def test_default_label_applied(self):
        check = Check()
        assert check.label == 'Check'

    def test_subclass_default_label_applied(self):
        class SubCheck(Check):
            pass

        check = SubCheck()
        assert check.label == 'Sub check'


class TestCheck:
    def test_default__status_is_disabled(self):
        check = Check()
        assert check.status == Status.DISABLED

    def test_default_update__status_is_disabled(self):
        check = Check()
        check.update()
        assert check.status == Status.DISABLED

    def test_custom_update__status_is_ok(self):
        check = MockCheck(Status.WARN)
        check.update()
        assert check.status == Status.WARN

    def test_update__status_is_ok(self):
        check = MockCheck()
        check.update()
        assert check.status == Status.OK

    def test_run__status_is_ok(self):
        check = MockCheck()
        status = check.run()
        assert status == check.status
        assert check.status == Status.OK


class TestSubcheck:
    def test_add__subcheck_added(self):
        check = Check()
        subcheck1 = Check()
        subcheck2 = Check()
        check.add(subcheck1)
        check.add(subcheck2)
        assert len(check.subchecks) == 2
        assert check.subchecks == [subcheck1, subcheck2]

    def test_add_multiple__subcheck_added(self):
        check = Check()
        subcheck1 = Check()
        subcheck2 = Check()
        check.add(subcheck1, subcheck2)
        assert len(check.subchecks) == 2
        assert check.subchecks == [subcheck1, subcheck2]

    def test_add__chains(self):
        check = Check()
        subcheck1 = Check()
        subcheck2 = Check()
        returned = check.add(subcheck1).add(subcheck2)
        assert returned == check
        assert len(check.subchecks) == 2
        assert check.subchecks == [subcheck1, subcheck2]

    def test_subcheck_bubbles_worst__worst_is_child(self):
        tree = MockCheck(Status.DISABLED).add(
            MockCheck(Status.OK).add(
                MockCheck(Status.DISABLED)
            ),
        )
        assert tree.run() == Status.OK
        assert tree.status == Status.OK

    def test_subcheck_bubbles_worst__worst_is_grandchild(self):
        tree = MockCheck(Status.DISABLED).add(
            MockCheck(Status.OK).add(
                MockCheck(Status.WARN)
            ),
        )
        assert tree.run() == Status.WARN
        assert tree.status == Status.WARN

    def test_subcheck_bubbles_worst__worst_is_child_sibling(self):
        tree = MockCheck(Status.DISABLED).add(
            MockCheck(Status.OK).add(
                MockCheck(Status.DISABLED)
            ),
            MockCheck(Status.ERROR),
        )
        assert tree.run() == Status.ERROR
        assert tree.status == Status.ERROR


class TestNotify:
    def test_notify__records_notifiers(self):
        check = Check()
        notifier1 = Notifier()
        notifier2 = Notifier()
        check.notify(notifier1)
        check.notify(notifier2)
        assert len(check.notifiers) == 2
        assert check.notifiers == [notifier1, notifier2]

    def test_notify_multiple__records_notifiers(self):
        check = Check()
        notifier1 = Notifier()
        notifier2 = Notifier()
        check.notify(notifier1, notifier2)
        assert len(check.notifiers) == 2
        assert check.notifiers == [notifier1, notifier2]

    def test_notify__chains(self):
        check = Check()
        notifier1 = Notifier()
        notifier2 = Notifier()
        returned = check.notify(notifier1).notify(notifier2)
        assert returned == check
        assert len(check.notifiers) == 2
        assert check.notifiers == [notifier1, notifier2]

    def test_run__does_not_notify(self):
        check = Check()
        notifier1 = MockNotifier()
        check.notify(notifier1)
        check.update()
        assert not notifier1.processed
        assert not notifier1.tested
        assert not notifier1.sent
