"""
Test disermo/storage/csv.py
"""
from disermo.constants import Status
from disermo.storage.csv import CSV


def read(path):
    with open(path, 'r') as file:
        lines = file.readlines()
    return lines


def write(path, lines):
    with open(path, 'w') as file:
        for line in lines:
            file.write(line)


def test_confirm_separator():
    # Tests will assume this
    assert CSV.SEPARATOR == '|'


def test_save(tmp_path):
    test_file = tmp_path / 'test.csv'
    storage = CSV(path=test_file)
    storage.set('key', Status.OK)
    storage.save()

    assert read(test_file) == [
        'key,1|1\n',
    ]


def test_save_multiple__appended(tmp_path):
    test_file = tmp_path / 'test.csv'
    storage = CSV(path=test_file)
    storage.set('key', Status.OK)
    storage.set('key', Status.WARN)
    storage.save()

    assert read(test_file) == [
        'key,1|1,2|1\n',
    ]


def test_save_different__all_set(tmp_path):
    test_file = tmp_path / 'test.csv'
    storage = CSV(path=test_file)
    storage.set('key1', Status.OK)
    storage.set('key1', Status.WARN)
    storage.set('key2', Status.ERROR)
    storage.save()

    assert read(test_file) == [
        'key1,1|1,2|1\n',
        'key2,3|1\n',
    ]


def test_load(tmp_path):
    test_file = tmp_path / 'test.csv'
    write(test_file, [
        'key1,1|1,2|1\n',
        'key2,3|1\n',
    ])

    storage = CSV(path=test_file)
    storage.load()

    assert storage.data == {
        'key1': [(Status.OK, 1), (Status.WARN, 1)],
        'key2': [(Status.ERROR, 1)],
    }


def test_load__does_not_exist__fail_silently(tmp_path):
    test_file = tmp_path / 'test.csv'
    storage = CSV(path=test_file)
    storage.load()

    assert storage.data == {}
