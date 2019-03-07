"""
Test disermo/storage/base.py
"""
from disermo.constants import Status
from disermo.storage.base import Storage


def test_set():
    storage = Storage()
    storage.set('key', Status.OK)
    assert storage.data == {'key': [(Status.OK, 1)]}


def test_set_multiple_different__appended():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    assert storage.data == {'key': [(Status.OK, 1), (Status.WARN, 1)]}


def test_set_multiple_same__incremented():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.OK)
    assert storage.data == {'key': [(Status.OK, 2)]}


def test_set_max__all_set():
    storage = Storage(max_memory=3)
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    assert storage.data == {
        'key': [(Status.OK, 1), (Status.WARN, 1), (Status.ERROR, 1)],
    }


def test_set_over_max__first_in_first_out():
    storage = Storage(max_memory=2)
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    assert storage.data == {'key': [(Status.WARN, 2), (Status.ERROR, 1)]}


def test_set_different__all_set():
    storage = Storage(max_memory=2)
    storage.set('key1', Status.OK)
    storage.set('key1', Status.WARN)
    storage.set('key2', Status.ERROR)
    assert storage.data == {
        'key1': [(Status.OK, 1), (Status.WARN, 1)],
        'key2': [(Status.ERROR, 1)],
    }


def test_get__returns_all():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    latest = storage.get('key')
    assert list(latest) == [Status.ERROR, Status.WARN, Status.OK]


def test_get_grouped__returns_groups():
    storage = Storage()
    storage.set('key', Status.OK)
    storage.set('key', Status.OK)
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.set('key', Status.ERROR)
    storage.set('key', Status.ERROR)
    latest = storage.get('key', grouped=True)
    assert list(latest) == [
        (Status.ERROR, 2),
        (Status.WARN, 1),
        (Status.OK, 3),
    ]
