"""
Test disermo/storage/base.py
"""
from disermo.constants import Status
from disermo.storage.base import Storage


def test_set():
    storage = Storage()
    storage.set('key', Status.OK)
    assert storage.data == {'key': [Status.OK]}


def test_set_multiple__appended():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    assert storage.data == {'key': [Status.OK, Status.WARN]}


def test_set_max__all_set():
    storage = Storage(max_memory=3)
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    assert storage.data == {'key': [Status.OK, Status.WARN, Status.ERROR]}


def test_set_over_max__first_in_first_out():
    storage = Storage(max_memory=2)
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    assert storage.data == {'key': [Status.WARN, Status.ERROR]}


def test_set_different__all_set():
    storage = Storage(max_memory=2)
    storage.set('key1', Status.OK)
    storage.set('key1', Status.WARN)
    storage.set('key2', Status.ERROR)
    assert storage.data == {
        'key1': [Status.OK, Status.WARN],
        'key2': [Status.ERROR],
    }


def test_latest__count_matches__returns_all():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    latest = storage.latest('key', 3)
    assert latest == [Status.OK, Status.WARN, Status.ERROR]


def test_latest__count_under__returns_subset():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    latest = storage.latest('key', 2)
    assert latest == [Status.WARN, Status.ERROR]


def test_latest__count_over__returns_all():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    latest = storage.latest('key', 5)
    assert latest == [Status.OK, Status.WARN, Status.ERROR]
